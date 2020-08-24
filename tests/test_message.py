import re

import pytest

from ..mailshake import EmailMessage


def test_ascii():
    email = EmailMessage("Subject", "Content", "from@example.com", "to@example.com")
    message = email.render()

    assert message["Subject"] == "Subject"
    assert message.get_payload() == "Content"
    assert message["From"] == "from@example.com"
    assert message["To"] == "to@example.com"


def test_multiple_recipients():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        ["to@example.com", "other@example.com"],
    )
    message = email.render()

    assert message["Subject"] == "Subject"
    assert message.get_payload() == "Content"
    assert message["From"] == "from@example.com"
    assert message["To"] == ("to@example.com, other@example.com")


def test_cc():
    email = EmailMessage("Subject", "Content", "from@example.com", cc="cc@example.com")
    message = email.render()

    assert message["Cc"] == "cc@example.com"
    assert not message["To"]
    assert not message["Bcc"]
    assert email.get_recipients() == ["cc@example.com"]


def test_multiple_cc():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        cc=["cc@example.com", "cc.other@example.com"],
    )
    message = email.render()

    print(message["Cc"])
    assert message["Cc"] == "cc@example.com, cc.other@example.com"
    assert not message["To"]
    assert not message["Bcc"]
    assert email.get_recipients() == ["cc@example.com", "cc.other@example.com"]


def test_bcc():
    email = EmailMessage(
        "Subject", "Content", "from@example.com", bcc="bcc@example.com"
    )
    message = email.render()

    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == ["bcc@example.com"]


def test_multiple_bcc():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        bcc=["bcc@example.com", "bcc.other@example.com"],
    )
    message = email.render()

    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == ["bcc@example.com", "bcc.other@example.com"]


def test_multiple_cc_and_to():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        to=["to@example.com", "other@example.com"],
        cc=["cc@example.com", "cc.other@example.com"],
    )
    message = email.render()

    assert message["To"] == "to@example.com, other@example.com"
    assert message["Cc"] == "cc@example.com, cc.other@example.com"
    assert not message["Bcc"]
    assert email.get_recipients() == [
        "to@example.com",
        "other@example.com",
        "cc@example.com",
        "cc.other@example.com",
    ]


def test_multiple_to_cc_bcc():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        to=["to@example.com", "other@example.com"],
        cc=["cc@example.com", "cc.other@example.com"],
        bcc=["bcc@example.com", "bcc.other@example.com"],
    )
    message = email.render()

    assert message["To"] == "to@example.com, other@example.com"
    assert message["Cc"] == "cc@example.com, cc.other@example.com"
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == [
        "to@example.com",
        "other@example.com",
        "cc@example.com",
        "cc.other@example.com",
        "bcc@example.com",
        "bcc.other@example.com",
    ]


def test_replyto():
    email = EmailMessage(
        "Subject", "Content", "from@example.com", reply_to="replyto@example.com"
    )
    message = email.render()

    assert message["Reply-To"] == "replyto@example.com"
    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == []


def test_multiple_replyto():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        reply_to=["replyto@example.com", "replyto.other@example.com"],
    )
    message = email.render()

    assert message["Reply-To"] == "replyto@example.com, replyto.other@example.com"
    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == []


def test_recipients_as_tuple():
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        to=("to@example.com", "other@example.com"),
        cc=("cc@example.com", "cc.other@example.com"),
        bcc=("bcc@example.com",),
    )
    message = email.render()

    assert message["To"] == "to@example.com, other@example.com"
    assert message["Cc"] == "cc@example.com, cc.other@example.com"
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == [
        "to@example.com",
        "other@example.com",
        "cc@example.com",
        "cc.other@example.com",
        "bcc@example.com",
    ]


def test_header_injection():
    email = EmailMessage(
        "Subject\nInjection Test", "Content", "from@example.com", "to@example.com"
    )
    with pytest.raises(ValueError):
        email.render()


def test_message_header_overrides():
    """Specifying dates or message-ids in the extra headers overrides the
    default values.
    """
    headers = {"date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"}
    email = EmailMessage(
        "Subject", "Content", "from@example.com", "to@example.com", headers=headers
    )

    email_as_string = email.as_string()
    assert email_as_string.startswith(
        'Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\n'
    )
    headers = [
        "Content-Transfer-Encoding: 7bit",
        "Subject: Subject",
        "From: from@example.com",
        "To: to@example.com",
        "date: Fri, 09 Nov 2001 01:08:47 -0000",
        "Message-ID: foo",
    ]
    lines = set(email_as_string.split("\n"))
    for header in headers:
        assert header in lines
    assert email_as_string.endswith("\n\nContent")


def test_from_header():
    """Make sure we can manually set the From header.
    """
    email = EmailMessage(
        "Subject",
        "Content",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    message = email.render()

    assert message["From"] == "from@example.com"


def test_multiple_message_call():
    """Make sure that headers are not changed when calling
    `EmailMessage.render()` again.
    """
    email = EmailMessage(
        "Subject",
        "Content",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    message = email.render()
    assert message["From"] == "from@example.com"
    message = email.render()
    assert message["From"] == "from@example.com"


def test_unicode_address_header():
    """When a to/from/cc header contains unicode,
    make sure the email addresses are parsed correctly (especially with
    regards to commas).
    """
    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        ['"Firstname Sürname" <to@example.com>', "other@example.com"],
    )
    message = email.render()
    assert (
        message["To"]
        == "=?utf-8?q?Firstname_S=C3=BCrname?= <to@example.com>, other@example.com"
    )

    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        ["other@example.com", '"Sürname, Firstname" <to@example.com>'],
    )
    message = email.render()
    assert (
        message["To"]
        == "other@example.com, =?utf-8?q?S=C3=BCrname=2C_Firstname?= <to@example.com>"
    )

    email = EmailMessage(
        "Subject",
        "Content",
        "from@example.com",
        ["other@example.com", "à" * 50 + " <to@example.com>"],
    )
    message = email.render()
    assert message["To"] == (
        "other@example.com, "
        + "=?utf-8?b?"
        + "w6DDoMOg" * 16
        + "w6DDoA==?= <to@example.com>"
    )


def test_unicode_headers():
    headers = {
        "Sender": '"Firstname Sürname" <sender@example.com>',
        "Comments": "My Sürname is non-ASCII",
    }
    email = EmailMessage(
        "Gżegżółka", "Content", "from@example.com", "to@example.com", headers=headers
    )
    message = email.render()

    assert message["Subject"] == "=?utf-8?b?R8W8ZWfFvMOzxYJrYQ==?="
    assert (
        message["Sender"] == "=?utf-8?q?Firstname_S=C3=BCrname?= <sender@example.com>"
    )
    assert message["Comments"] == "=?utf-8?q?My_S=C3=BCrname_is_non-ASCII?="


def test_html():
    subject = "hello"
    from_email = "from@example.com"
    to = "to@example.com"
    text_content = "This is an important message."
    html_content = "<p>This is an <strong>important</strong> message.</p>"

    email = EmailMessage(
        subject, text_content, from_email, to, html_content=html_content
    )
    message = email.render()

    assert message.is_multipart()
    assert message.get_content_type() == "multipart/alternative"
    assert message.get_default_type() == "text/plain"
    assert message.get_payload(0).get_content_type() == "text/plain"
    assert message.get_payload(1).get_content_type() == "text/html"


def test_safe_mime_multipart():
    """Make sure headers can be set with a different encoding than utf-8 in
    SafeMIMEMultipart as well
    """
    subject = "Message from Firstname Sürname"
    from_email = "from@example.com"
    to = '"Sürname, Firstname" <to@example.com>'
    text_content = "This is an important message."
    html_content = "<p>This is an <strong>important</strong> message.</p>"
    headers = {"Date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"}

    email = EmailMessage(
        subject,
        text_content,
        from_email,
        to,
        html_content=html_content,
        headers=headers,
    )
    email.encoding = "iso-8859-1"
    email.render()


def test_encoding():
    """Encode body correctly with other encodings
    than utf-8
    """
    email = EmailMessage(
        "Subject",
        "Firstname Sürname is a great guy.",
        "from@example.com",
        "other@example.com",
    )
    email.encoding = "iso-8859-1"
    message = email.render()

    assert message.as_string().startswith(
        'Content-Type: text/plain; charset="iso-8859-1"'
        "\nMIME-Version: 1.0"
        "\nContent-Transfer-Encoding: quoted-printable"
        "\nSubject: Subject"
        "\nFrom: from@example.com"
        "\nTo: other@example.com"
    )
    assert message.get_payload() == "Firstname S=FCrname is a great guy."

    # Make sure MIME attachments also works correctly with other encodings than utf-8
    text_content = "Firstname Sürname is a great guy."
    html_content = "<p>Firstname Sürname is a <strong>great</strong> guy.</p>"

    email = EmailMessage(
        "Subject",
        text_content,
        "from@example.com",
        "to@example.com",
        html_content=html_content,
    )
    email.encoding = "iso-8859-1"
    message = email.render()

    assert message.get_payload(0).as_string() == (
        'Content-Type: text/plain; charset="iso-8859-1"'
        "\nMIME-Version: 1.0"
        "\nContent-Transfer-Encoding: quoted-printable"
        "\n\nFirstname S=FCrname is a great guy."
    )
    assert message.get_payload(1).as_string() == (
        'Content-Type: text/html; charset="iso-8859-1"'
        "\nMIME-Version: 1.0"
        "\nContent-Transfer-Encoding: quoted-printable"
        "\n\n<p>Firstname S=FCrname is a <strong>great</strong> guy.</p>"
    )


def test_attachments():
    subject = "hello"
    from_email = "from@example.com"
    to = "to@example.com"
    text_content = "This is an important message."
    html_content = "<p>This is an <strong>important</strong> message.</p>"

    email = EmailMessage(
        subject, text_content, from_email, to, html_content=html_content
    )
    email.attach("an attachment.pdf", "%PDF-1.4.%...", mimetype="application/pdf")
    message = email.render()

    assert message.is_multipart()
    assert message.get_content_type() == "multipart/mixed"
    assert message.get_default_type() == "text/plain"
    assert message.get_payload(0).get_content_type() == "multipart/alternative"
    assert message.get_payload(1).get_content_type() == "application/pdf"


def test_dont_mangle_from_in_body():
    """Make sure that EmailMessage doesn't mangle 'From' in message body."""
    email = EmailMessage(
        "Subject",
        "From the future",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    str_email = email.as_bytes()
    print(str_email)
    assert b">From the future" not in str_email


def test_dont_base64_encode():
    """Shouldn't use Base64 encoding at all.
    """
    email = EmailMessage(
        "Subject",
        "UTF-8 encoded body",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    assert "Content-Transfer-Encoding: base64" not in email.as_string()


def test_7bit_no_quoted_printable():
    """Shouldn't use quoted printable, should detect it can represent content
    with 7 bit data.
    """
    email = EmailMessage(
        "Subject",
        "Body with only ASCII characters.",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    msg = email.as_string()

    assert "Content-Transfer-Encoding: quoted-printable" not in msg
    assert "Content-Transfer-Encoding: 7bit" in msg


def test_8bit_no_quoted_printable():
    """Shouldn't use quoted printable, should detect it can represent content
    with 8 bit data.
    """
    email = EmailMessage(
        "Subject",
        "Body with latin characters: àáä.",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    msg = email.as_string()

    assert "Content-Transfer-Encoding: quoted-printable" not in msg
    assert "Content-Transfer-Encoding: 8bit" in msg

    email = EmailMessage(
        "Subject",
        "Body with non latin characters: А Б В Г Д Е Ж Ѕ З И І К Л М Н О П.",
        "bounce@example.com",
        "to@example.com",
        headers={"From": "from@example.com"},
    )
    msg = email.as_string()

    assert "Content-Transfer-Encoding: quoted-printable" not in msg
    assert "Content-Transfer-Encoding: 8bit" in msg


def test_invalid_destination():
    dest = "toБ@example.com"
    email = EmailMessage("Subject", "Content", "from@example.com", dest)
    message = email.render()

    assert message["Subject"] == "Subject"
    assert message.get_payload() == "Content"
    assert message["From"] == "from@example.com"
    assert message["To"] != dest


def test_message_id():
    message_id_re = re.compile(
        r"^<[0-9]{14}\.[0-9]+\.[0-9a-f]+\.[0-9]+@[a-z\-]+(\.[a-z\-]+)*>$",
        re.IGNORECASE
    )
    email1 = EmailMessage("Subject 1", "Content", "from@example.com", "to@example.com")
    msg1 = email1.render()
    assert message_id_re.match(msg1["Message-ID"])
    email2 = EmailMessage("Subject 2", "Content", "from@example.com", "to@example.com")
    msg2 = email2.render()
    assert message_id_re.match(msg2["Message-ID"])
    assert msg2["Message-ID"] != msg1["Message-ID"]
