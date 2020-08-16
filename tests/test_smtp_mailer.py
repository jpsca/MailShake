import asyncore
from email import message_from_bytes
import smtpd
from smtplib import SMTPException
import threading

import pytest

from ..mailshake import EmailMessage, SMTPMailer


def make_emails():
    return [
        EmailMessage(
            "Subject-%s" % num, "Content", "from@example.com", "to@example.com"
        )
        for num in range(1, 5)
    ]


smtp_server = None
SMTP_HOST = "127.0.0.1"
SMTP_PORT = 8080


class FakeSMTPServer(smtpd.SMTPServer):
    """A Fake smtp server"""

    def __init__(self, host, port):
        print("Running fake SMTP server")
        localaddr = (host, port)
        remoteaddr = None
        smtpd.SMTPServer.__init__(self, localaddr, remoteaddr)
        self.flush_sink()

    def flush_sink(self):
        self.sink = []

    def process_message(self, peer, from_, to, bmessage, **kwargs):
        self.sink.append(message_from_bytes(bmessage))

    def start(self):
        # timeout parameter is important, otherwise code will block 30 seconds after
        # the SMTP channel has been closed
        self.thread = threading.Thread(target=asyncore.loop, kwargs={"timeout": 0.1})
        self.thread.start()

    def stop(self):
        # close the SMTPserver to ensure no channels connect to asyncore
        self.close()
        # now it is save to wait for the thread to finish,
        # i.e. for asyncore.loop() to exit
        self.thread.join()


def setup_module():
    global smtp_server
    smtp_server = FakeSMTPServer(SMTP_HOST, SMTP_PORT)
    smtp_server.start()


def teardown_module():
    global smtp_server
    if smtp_server is not None:
        smtp_server.stop()


def test_sending():
    global smtp_server
    smtp_server.flush_sink()

    mailer = SMTPMailer(host=SMTP_HOST, port=SMTP_PORT, use_tls=False)
    email1, email2, email3, email4 = make_emails()

    assert mailer.send_messages(email1) == 1
    assert mailer.send_messages(email2, email3) == 2
    assert mailer.send_messages(email4) == 1

    sink = smtp_server.sink
    assert len(sink) == 4

    message = sink[0]
    print(message)
    assert message.get_content_type() == "text/plain"
    assert message.get("subject") == "Subject-1"
    assert message.get("from") == "from@example.com"
    assert message.get("to") == "to@example.com"


def test_sending_unicode():
    global smtp_server
    smtp_server.flush_sink()

    mailer = SMTPMailer(host="127.0.0.1", port=SMTP_PORT, use_tls=False)
    email = EmailMessage(
        "Olé", "Contenido en español", "from@example.com", "toБ@example.com"
    )
    assert mailer.send_messages(email)
    sink = smtp_server.sink
    assert len(sink) == 1


def test_notls():
    with pytest.raises(SMTPException):
        mailer = SMTPMailer(host="127.0.0.1", port=SMTP_PORT, use_tls=True)
        mailer.open()


def test_wrong_host():
    with pytest.raises(Exception):
        mailer = SMTPMailer(host="123", port=SMTP_PORT, use_tls=False, timeout=0.5)
        mailer.open()


def test_wrong_port():
    with pytest.raises(Exception):
        mailer = SMTPMailer(host="127.0.0.1", port=3000, use_tls=False)
        mailer.open()


def test_fail_silently():
    mailer = SMTPMailer(
        host="127.0.0.1", port=SMTP_PORT, use_tls=True, fail_silently=True
    )
    mailer.open()

    mailer = SMTPMailer(host="123", port=SMTP_PORT, use_tls=False, fail_silently=True, timeout=0.5)
    mailer.open()

    mailer = SMTPMailer(host="127.0.0.1", port=3000, use_tls=False, fail_silently=True)
    mailer.open()


def test_batch_too_many_recipients():
    global smtp_server
    smtp_server.flush_sink()

    mailer = SMTPMailer(
        host="127.0.0.1", port=SMTP_PORT, use_tls=False, max_recipients=200
    )
    send_to = ["user{}@example.com".format(i) for i in range(1, 1501)]
    msg = EmailMessage("The Subject", "Content", "from@example.com", send_to)

    assert mailer.send_messages(msg) == 1
    sink = smtp_server.sink
    assert len(sink) == 8

    assert len(sink[0].get("to").split(",")) == 200
    assert len(sink[1].get("to").split(",")) == 200
    assert len(sink[2].get("to").split(",")) == 200
    assert len(sink[3].get("to").split(",")) == 200
    assert len(sink[4].get("to").split(",")) == 200
    assert len(sink[5].get("to").split(",")) == 200
    assert len(sink[6].get("to").split(",")) == 200
    assert len(sink[7].get("to").split(",")) == 100
