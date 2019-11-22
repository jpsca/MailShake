from io import StringIO
import sys

import pytest

from mailshake import EmailMessage, BaseMailer, ToMemoryMailer, ToConsoleMailer


def test_base_mailer():
    mailer = BaseMailer()
    mailer.open()
    mailer.close()
    with pytest.raises(NotImplementedError):
        mailer.send()


def test_to_memory_mailer():
    mailer = ToMemoryMailer()
    email1, email2, email3, email4 = [
        EmailMessage(
            "Subject",
            f"The text of this email #{num}",
            "from@example.com",
            "to@example.com",
        )
        for num in range(1, 5)
    ]

    assert mailer.send_messages(email1) == 1
    assert mailer.send_messages(email2, email3, email4) == 3
    assert len(mailer.outbox) == 4
    assert mailer.outbox[1] == email2


def test_to_console_mailer():
    __stdout = sys.stdout
    try:
        stdout = sys.stdout = StringIO()
        mailer = ToConsoleMailer()
        mailer.send("Subject", "Content", "from@example.com", "to@example.com")
        value = stdout.getvalue()
    finally:
        sys.stdout = __stdout

    print(value)
    assert value.startswith(
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: 7bit\n"
        "MIME-Version: 1.0\n"
        "Subject: Subject\n"
        'From: "from@example.com"\n'
        'To: "to@example.com"\n'
    )
    mailer.send_messages()


def test_to_console_mailer_no_stream():
    mailer = ToConsoleMailer()
    mailer.stream = ""
    with pytest.raises(Exception):
        mailer.send("Subject", "Content", "from@example.com", "to@example.com")


def test_to_console_mailer_fail_silently():
    mailer = ToConsoleMailer()
    mailer.stream = ""
    mailer.fail_silently = True
    mailer.send("Subject", "Content", "from@example.com", "to@example.com")


def test_to_console_stream_kwarg():
    """Test that the console backend can be pointed at an arbitrary stream.
    """
    s = StringIO()
    mailer = ToConsoleMailer(stream=s)
    mailer.send("Subject", "Content", "from@example.com", "to@example.com")

    value = s.getvalue()
    assert value.startswith(
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: 7bit\n"
        "MIME-Version: 1.0\n"
        "Subject: Subject\n"
        'From: "from@example.com"\n'
        'To: "to@example.com"\n'
    )
