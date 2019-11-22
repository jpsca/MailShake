import pytest

from mailshake import EmailMessage


def test_ascii():
    email = EmailMessage("Subject", "Content", "from@example.com", "to@example.com")
    message = email.render()

    assert message["Subject"] == "Subject"
    assert message.get_payload() == "Content\n"
    assert message["From"] == '"from@example.com"'
    assert message["To"] == '"to@example.com"'


def test_multiple_recipients():
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        to=["to@example.com", "other@example.com"],
    )
    message = email.render()

    assert message["Subject"] == "Subject"
    assert message.get_payload() == "Content\n"
    assert message["From"] == '"from@example.com"'
    assert message["To"] == '"to@example.com", "other@example.com"'


def test_cc():
    email = EmailMessage("Subject", "Content", "from@example.com", cc="cc@example.com")
    message = email.render()

    assert message["Cc"] == '"cc@example.com"'
    assert not message["To"]
    assert not message["Bcc"]
    assert email.get_recipients() == ["cc@example.com"]


def test_multiple_cc():
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        cc=["cc@example.com", "cc.other@example.com"],
    )
    message = email.render()

    print(message["Cc"])
    assert message["Cc"] == '"cc@example.com", "cc.other@example.com"'
    assert not message["To"]
    assert not message["Bcc"]
    assert email.get_recipients() == ["cc@example.com", "cc.other@example.com"]


def test_bcc():
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        bcc="bcc@example.com",
    )
    message = email.render()

    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == ["bcc@example.com"]


def test_multiple_bcc():
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        bcc=["bcc@example.com", "bcc.other@example.com"],
    )
    message = email.render()

    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == ["bcc@example.com", "bcc.other@example.com"]


def test_multiple_to_cc_bcc():
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        to=["to@example.com", "other@example.com"],
        cc=["cc@example.com", "cc.other@example.com"],
        bcc=["bcc@example.com", "bcc.other@example.com"],
    )
    message = email.render()

    assert message["To"] == '"to@example.com", "other@example.com"'
    assert message["Cc"] == '"cc@example.com", "cc.other@example.com"'
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
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        reply_to="replyto@example.com",
    )
    message = email.render()

    assert message["Reply-To"] == '"replyto@example.com"'
    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == []


def test_multiple_replyto():
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        reply_to=["replyto@example.com", "replyto.other@example.com"],
    )
    message = email.render()

    assert message["Reply-To"] == '"replyto@example.com", "replyto.other@example.com"'
    assert not message["To"]
    assert not message["Cc"]
    assert not message["Bcc"]  # as it should
    assert email.get_recipients() == []


def test_header_injection():
    email = EmailMessage(
        subject="Subject\nInjection Test",
        text="Content",
        from_email="from@example.com",
        to="to@example.com",
    )
    with pytest.raises(ValueError):
        email.render()


def test_message_header_overrides():
    """Specifying dates or message-ids in the extra headers overrides the
    default values.
    """
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="from@example.com",
        to="to@example.com",
        headers={"date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"},
    )

    email_as_string = email.as_string()
    print(email_as_string)
    lines = [
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: 7bit\n",
        "MIME-Version: 1.0\n",
        "Subject: Subject\n",
        'From: "from@example.com"\n',
        'To: "to@example.com"\n',
        "Cc:\n",
        "Reply-To:\n",
        "date: Fri, 09 Nov 2001 01:08:47 -0000\n",
        "Message-ID: foo\n",
        "\n",
        "Content",
    ]
    for line in lines:
        assert line in email_as_string


def test_multiple_message_call():
    """Make sure that headers are not changed when calling
    `EmailMessage.render()` again.
    """
    email = EmailMessage(
        subject="Subject",
        text="Content",
        from_email="bounce@example.com",
        to="to@example.com",
        headers={"foo": "bar"},
    )
    message = email.render()
    assert message["foo"] == "bar"
    message = email.render()
    assert message["foo"] == "bar"


def test_html():
    email = EmailMessage(
        subject="hello",
        from_email="from@example.com",
        to="to@example.com",
        text="This is an important message.",
        html="<p>This is an <strong>important</strong> message.</p>",
    )
    message = email.render()

    assert message.is_multipart()
    assert message.get_content_type() == "multipart/alternative"
    assert message.get_default_type() == "text/plain"
    assert message.get_payload(0).get_content_type() == "text/plain"
    assert message.get_payload(1).get_content_type() == "text/html"


def test_not_utf8():
    email = EmailMessage(
        subject="Subject",
        text="Firstname Sürname is a great guy.",
        from_email="from@example.com",
        to="other@example.com",
    )
    email.encoding = "iso-8859-1"
    message = email.render()

    as_string = message.as_string()
    print(as_string)
    assert as_string.startswith(
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: base64\n"
        "MIME-Version: 1.0\n"
        "Subject: Subject\n"
        'From: "from@example.com"\n'
        'To: "other@example.com"\n'
    )
    assert message.get_payload() == "Firstname Sürname is a great guy.\n"


def test_not_utf8_mime_attachments():
    email = EmailMessage(
        subject="Subject",
        text="Firstname Sürname is a great guy.",
        html="<p>Firstname Sürname is a <strong>great</strong> guy.</p>",
        from_email="from@example.com",
        to="to@example.com",
    )
    email.encoding = "iso-8859-1"
    message = email.render()

    payload_as_string = message.get_payload(0).as_string()
    print(payload_as_string)
    assert payload_as_string.startswith(
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: base64\n"
    )

    payload_as_string = message.get_payload(1).as_string()
    print(payload_as_string)
    assert payload_as_string.startswith(
        'Content-Type: text/html; charset="utf-8"\n'
        "Content-Transfer-Encoding: base64\n"
    )


def test_attachments():
    email = EmailMessage(
        subject="hello",
        from_email="from@example.com",
        to="to@example.com",
        text="This is an important message.",
        html="<p>This is an <strong>important</strong> message.</p>",
    )
    email.attach("an attachment.pdf", "%PDF-1.4.%...", mimetype="application/pdf")
    message = email.render()

    assert message.is_multipart()
    assert message.get_content_type() == "multipart/mixed"
    assert message.get_default_type() == "text/plain"
    assert message.get_payload(0).get_content_type() == "multipart/alternative"
    assert message.get_payload(1).get_content_type() == "application/pdf"


def test_dont_base64_encode():
    email = EmailMessage(
        subject="Subject",
        text="UTF-8 encoded body",
        from_email="bounce@example.com",
        to="to@example.com",
    )
    assert "Content-Transfer-Encoding: base64" not in email.as_string()


def test_invalid_destination():
    dest = "toБ@example.com"
    email = EmailMessage(
        subject="Subject", text="Content", from_email="from@example.com", to=dest
    )
    message = email.render()

    assert message["Subject"] == "Subject"
    assert message.get_payload() == "Content\n"
    assert message["From"] == '"from@example.com"'
    assert message["To"] != f'"#{dest}"'
    assert message["To"] != dest
