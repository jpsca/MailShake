# coding=utf-8
from __future__ import print_function
import asyncore
import smtpd
from smtplib import SMTPException
import threading

from mailshake._compat import PY3
from mailshake import EmailMessage, SMTPMailer
import pytest

if PY3:
    from email.utils import parseaddr
    from email import message_from_bytes
else:
    from email.Utils import parseaddr
    from email import message_from_string as message_from_bytes


def make_emails():
    return [
        EmailMessage('Subject-%s' % num, 'Content',
                     'from@example.com', 'to@example.com')
        for num in range(1, 5)
    ]


class FakeSMTPChannel(smtpd.SMTPChannel):

    def collect_incoming_data(self, data):
        try:
            super(FakeSMTPChannel, self).collect_incoming_data(data)
        except UnicodeDecodeError:
            # ignore decode error in SSL/TLS connection tests as we only care
            # whether the connection attempt was made
            pass


class FakeSMTPServer(smtpd.SMTPServer, threading.Thread):
    """
    Asyncore SMTP server wrapped into a thread. Based on DummyFTPServer from:
    http://svn.python.org/view/python/branches/py3k/Lib/test/test_ftplib.py?revision=86061&view=markup
    """
    channel_class = FakeSMTPChannel

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        smtpd.SMTPServer.__init__(self, *args, **kwargs)
        self._sink = []
        self.active = False
        self.active_lock = threading.Lock()
        self.sink_lock = threading.Lock()

    def process_message(self, peer, mailfrom, rcpttos, data):
        if PY3:
            data = data.encode('utf-8')
        m = message_from_bytes(data)
        maddr = parseaddr(m.get('from'))[1]
        if mailfrom != maddr:
            return "553 '%s' != '%s'" % (mailfrom, maddr)
        with self.sink_lock:
            self._sink.append(m)

    def get_sink(self):
        with self.sink_lock:
            return self._sink[:]

    def flush_sink(self):
        with self.sink_lock:
            self._sink[:] = []

    def start(self):
        assert not self.active
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    def run(self):
        self.active = True
        self.__flag.set()
        while self.active and asyncore.socket_map:
            with self.active_lock:
                asyncore.loop(timeout=0.1, count=1)
        asyncore.close_all()

    def stop(self):
        if self.active:
            self.active = False
            self.join()


server = None


def setup_module():
    global server
    server = FakeSMTPServer(('127.0.0.1', 8000), None)
    server.start()


def teardown_module():
    global server
    if server is not None:
        server.flush_sink()
        server.stop()


# def test_sending():
#     global server
#     server.flush_sink()

#     mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=False)
#     email1, email2, email3, email4 = make_emails()

#     assert mailer.send_messages(email1) == 1
#     assert mailer.send_messages(email2, email3) == 2
#     assert mailer.send_messages(email4) == 1

#     sink = server.get_sink()
#     assert len(sink) == 4

#     message = sink[0]
#     print(message)
#     assert message.get_content_type() == 'text/plain'
#     assert message.get('subject') == 'Subject-1'
#     assert message.get('from') == 'from@example.com'
#     assert message.get('to') == 'to@example.com'


# def test_sending_unicode():
#     global server
#     server.flush_sink()

#     mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=False)
#     email = EmailMessage(
#         u'Olé',
#         u'Contenido en español',
#         u'from@example.com',
#         u'to@example.com'
#     )
#     assert mailer.send_messages(email)
#     sink = server.get_sink()
#     assert len(sink) == 1


# def test_notls():
#     with pytest.raises(SMTPException):
#         mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=True)
#         mailer.open()


# def test_wrong_host():
#     with pytest.raises(Exception):
#         mailer = SMTPMailer(host='123', port=8000, use_tls=False)
#         mailer.open()


# def test_wrong_port():
#     with pytest.raises(Exception):
#         mailer = SMTPMailer(host='127.0.0.1', port=3000, use_tls=False)
#         mailer.open()


# def test_fail_silently():
#     mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=True,
#                         fail_silently=True)
#     mailer.open()

#     mailer = SMTPMailer(host='123', port=8000, use_tls=False,
#                         fail_silently=True)
#     mailer.open()

#     mailer = SMTPMailer(host='127.0.0.1', port=3000, use_tls=False,
#                         fail_silently=True)
#     mailer.open()


def test_batch_too_many_recipients():
    global server
    server.flush_sink()

    mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=False)
    send_to = ['user{}@example.com'.format(i) for i in range(1, 1501)]
    msg = EmailMessage('The Subject', 'Content', 'from@example.com', send_to)

    assert mailer.send_messages(msg) == 1
    sink = server.get_sink()
    assert len(sink) == 2

    email1 = sink[0]
    email2 = sink[1]
    assert len(email1.get('to').split(',')) == 1000
    assert len(email2.get('to').split(',')) == 500
