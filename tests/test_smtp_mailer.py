import pytest
from smtplib import SMTP, SMTPException

from ..mailshake import EmailMessage, SMTPMailer


def make_emails():
    return [
        EmailMessage(
            "Subject-%s" % num, "Content", "from@example.com", "to@example.com"
        )
        for num in range(1, 5)
    ]


def test_sending(smtpd):
    mailer = SMTPMailer(host=smtpd.hostname, port=smtpd.port, use_tls=False)
    email1, email2, email3, email4 = make_emails()

    with SMTP(smtpd.hostname, smtpd.port):
        assert mailer.send_messages(email1) == 1
        assert mailer.send_messages(email2, email3) == 2
        assert mailer.send_messages(email4) == 1

    assert len(smtpd.messages) == 4

    message = smtpd.messages[0]
    print(message)
    assert message.get_content_type() == "text/plain"
    assert message.get("subject") == "Subject-1"
    assert message.get("from") == "from@example.com"
    assert message.get("to") == "to@example.com"


def test_sending_unicode(smtpd):
    mailer = SMTPMailer(host=smtpd.hostname, port=smtpd.port, use_tls=False)
    email = EmailMessage(
        subject="Olé",
        text="Contenido en español",
        from_email="from@example.com",
        to="toБ@example.com",
    )

    with SMTP(smtpd.hostname, smtpd.port):
        assert mailer.send_messages(email)

    assert len(smtpd.messages) == 1
    message = smtpd.messages[0]
    print(message)
    assert message.get_content_type() == "text/plain"
    assert message.get("subject") == "=?utf-8?q?Ol=C3=A9?="


def test_notls(smtpd):
    mailer = SMTPMailer(host=smtpd.hostname, port=smtpd.port, use_tls=True)
    with pytest.raises(SMTPException):
        with SMTP(smtpd.hostname, smtpd.port):
            mailer.open()
    mailer.close()


def test_wrong_host(smtpd):
    mailer = SMTPMailer(host="123", port=smtpd.port, use_tls=False, timeout=0.5)
    with pytest.raises(Exception):
        with SMTP(smtpd.hostname, smtpd.port):
            mailer.open()
    mailer.close()


def test_wrong_port(smtpd):
    mailer = SMTPMailer(host=smtpd.hostname, port=3000, use_tls=False)
    with pytest.raises(Exception):
        with SMTP(smtpd.hostname, smtpd.port):
            mailer.open()
    mailer.close()


def test_fail_silently(smtpd):
    mailer = SMTPMailer(
        host=smtpd.hostname,
        port=smtpd.port,
        use_tls=True,
        fail_silently=True,
    )
    with SMTP(smtpd.hostname, smtpd.port):
        mailer.open()
    mailer.close()

    mailer = SMTPMailer(
        host="123",
        port=smtpd.port,
        use_tls=False,
        fail_silently=True,
        timeout=0.5,
    )
    with SMTP(smtpd.hostname, smtpd.port):
        mailer.open()
    mailer.close()

    mailer = SMTPMailer(
        host=smtpd.hostname,
        port=3000,
        use_tls=False,
        fail_silently=True,
    )
    with SMTP(smtpd.hostname, smtpd.port):
        mailer.open()
    mailer.close()


def test_batch_too_many_recipients(smtpd):
    mailer = SMTPMailer(
        host=smtpd.hostname,
        port=smtpd.port,
        use_tls=False,
        max_recipients=200,
    )
    send_to = ["user{}@example.com".format(i) for i in range(1, 1501)]
    msg = EmailMessage("The Subject", "Content", "from@example.com", send_to)

    with SMTP(smtpd.hostname, smtpd.port):
        assert mailer.send_messages(msg) == 1

    assert len(smtpd.messages) == 8
    assert len(smtpd.messages[0].get("to").split(",")) == 200
    assert len(smtpd.messages[1].get("to").split(",")) == 200
    assert len(smtpd.messages[2].get("to").split(",")) == 200
    assert len(smtpd.messages[3].get("to").split(",")) == 200
    assert len(smtpd.messages[4].get("to").split(",")) == 200
    assert len(smtpd.messages[5].get("to").split(",")) == 200
    assert len(smtpd.messages[6].get("to").split(",")) == 200
    assert len(smtpd.messages[7].get("to").split(",")) == 100
