# -*- coding: utf-8 -*-
"""
    SMTPMailer tests.
"""
import asyncore
from datetime import datetime
import email
import smtpd
from smtplib import SMTPException
import threading

import mailshake
from mailshake import EmailMessage
from mailshake.mailers.smtp import SMTPMailer
import pytest


def make_emails():
    return [EmailMessage('Subject-%s' % num, 'Content',
        'from@example.com', 'to@example.com') for num in range(1, 5)]


class FakeSMTPServer(smtpd.SMTPServer, threading.Thread):
    """Asyncore SMTP server wrapped into a thread.
    Based on DummyFTPServer from:
    http://svn.python.org/view/python/branches/py3k/Lib/test/test_ftplib.py?revision=86061&view=markup
    """

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        smtpd.SMTPServer.__init__(self, *args, **kwargs)
        self._sink = []
        self.active = False
        self.active_lock = threading.Lock()
        self.sink_lock = threading.Lock()
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        m = email.message_from_string(data)
        maddr = email.Utils.parseaddr(m.get('from'))[1]
        if mailfrom != maddr:
            return "553 '%s' != '%s'" % (mailfrom, maddr)
        self.sink_lock.acquire()
        self._sink.append(m)
        self.sink_lock.release()
    
    def get_sink(self):
        self.sink_lock.acquire()
        try:
            return self._sink[:]
        finally:
            self.sink_lock.release()
    
    def flush_sink(self):
        self.sink_lock.acquire()
        self._sink[:] = []
        self.sink_lock.release()
    
    def start(self):
        assert not self.active
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()
    
    def run(self):
        self.active = True
        self.__flag.set()
        while self.active and asyncore.socket_map:
            self.active_lock.acquire()
            asyncore.loop(timeout=0.1, count=1)
            self.active_lock.release()
        asyncore.close_all()
    
    def stop(self):
        assert self.active
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


def test_sending():
    global server
    server.flush_sink()
    
    mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=False)
    email1, email2, email3, email4 = make_emails()

    assert mailer.send(email1) == 1
    assert mailer.send(email2, email3) == 2
    assert mailer.send(email4) == 1

    sink = server.get_sink()
    assert len(sink) == 4

    message = sink[0]
    print message
    assert message.get_content_type() == 'text/plain'
    assert message.get('subject') == 'Subject-1'
    assert message.get('from') == 'from@example.com'
    assert message.get('to') == 'to@example.com'


def test_notls():
    with pytest.raises(SMTPException):
        mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=True)
        mailer.open()


def test_wrong_host():
    with pytest.raises(Exception):
        mailer = SMTPMailer(host='123', port=8000, use_tls=False)
        mailer.open()


def test_wrong_port():
    with pytest.raises(Exception):
        mailer = SMTPMailer(host='127.0.0.1', port=3000, use_tls=False)
        mailer.open()


def test_fail_silently():
    mailer = SMTPMailer(host='127.0.0.1', port=8000, use_tls=True,
        fail_silently=True)
    mailer.open()
    
    mailer = SMTPMailer(host='123', port=8000, use_tls=False,
        fail_silently=True)
    mailer.open()

    mailer = SMTPMailer(host='127.0.0.1', port=3000, use_tls=False,
        fail_silently=True)
    mailer.open()

