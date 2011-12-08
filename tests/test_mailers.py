# -*- coding: utf-8 -*-
"""
    Mailers tests.
"""
from datetime import datetime
import email
import os
import shutil
from StringIO import StringIO
import shutil
import sys
import tempfile

import mailshake
from mailshake import EmailMessage
from mailshake.mailers.dummy import DummyMailer
from mailshake.mailers.memory import ToMemoryMailer
from mailshake.mailers.console import ToConsoleMailer
from mailshake.mailers.filebased import ToFileMailer
from mailshake.mailers.smtp import SMTPMailer
import pytest


def make_emails():
    return [EmailMessage('Subject', 'Content #%s' % content, 'from@example.com',
        'to@example.com') for content in range(1, 5)]


def test_dummy_mailer():
    mailer = DummyMailer()
    email1, email2, email3, email4 = make_emails()

    assert mailer.send(email1) == 1
    assert mailer.send(email2, email3, email4) == 3


def test_to_memory_mailer():
    mailer = ToMemoryMailer()
    email1, email2, email3, email4 = make_emails()

    assert mailer.send(email1) == 1
    assert mailer.send(email2, email3, email4) == 3
    assert len(mailer.outbox) == 4
    assert mailer.outbox[1] == email2


def test_to_console_mailer():
    __stdout = sys.stdout
    s = sys.stdout = StringIO()

    mailer = ToConsoleMailer()
    email1 = EmailMessage('Subject', 'Content', 'from@example.com',
        'to@example.com')
    mailer.send(email1)

    value = s.getvalue()
    assert value.startswith('Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Subject\nFrom: from@example.com\nTo: to@example.com\nDate: ')

    sys.stdout = __stdout


def test_to_console_stream_kwarg():
    """Test that the console backend can be pointed at an arbitrary stream.
    """
    s = StringIO()
    mailer = ToConsoleMailer(stream=s)
    email1 = EmailMessage('Subject', 'Content', 'from@example.com',
        'to@example.com')
    mailer.send(email1)

    value = s.getvalue()
    assert value.startswith('Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Subject\nFrom: from@example.com\nTo: to@example.com\nDate: ')


def test_to_file_mailer():
    tmp_dir = tempfile.mkdtemp()
    mailer = ToFileMailer(tmp_dir)
    email1 = EmailMessage('Subject', 'Content', 'from@example.com',
        'to@example.com')
    
    assert mailer.send(email1) == 1
    assert len(os.listdir(tmp_dir)) == 1

    filepath = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])
    message = email.message_from_file(open(filepath))
    
    assert message.get_content_type() == 'text/plain'
    assert message.get('subject') == 'Subject'
    assert message.get('from') == 'from@example.com'
    assert message.get('to') == 'to@example.com'

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_dir_creation():
    tmp_dir = os.path.join(os.path.dirname(__file__), 'qwertyuiop12345')
    mailer = ToFileMailer(tmp_dir)

    assert os.path.isdir(tmp_dir)

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_unique_filename():
    tmp_dir = tempfile.mkdtemp()
    mailer1 = ToFileMailer(tmp_dir)
    mailer2 = ToFileMailer(tmp_dir)
    email1 = EmailMessage('Subject', 'Content', 'from@example.com',
        'to@example.com')
    mailer1.send(email1)
    mailer2.send(email1)

    assert len(os.listdir(tmp_dir)) == 2

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_one_file():
    tmp_dir = tempfile.mkdtemp()
    mailer = ToFileMailer(tmp_dir, multifile=False)
    email1, email2, email3, email4 = make_emails()
    
    assert mailer.send(email1) == 1
    assert mailer.send(email2, email3) == 2
    assert mailer.send(email4) == 1
    assert len(os.listdir(tmp_dir)) == 1

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_multifile():
    tmp_dir = tempfile.mkdtemp()
    mailer = ToFileMailer(tmp_dir, multifile=True)
    email1, email2, email3, email4 = make_emails()

    assert mailer.send(email1) == 1
    assert mailer.send(email2, email3) == 2
    assert mailer.send(email4) == 1
    assert len(os.listdir(tmp_dir)) == 3

    shutil.rmtree(tmp_dir, True)

