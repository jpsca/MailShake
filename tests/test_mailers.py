# coding=utf-8
from __future__ import print_function
import email
import os
import shutil
import sys
import tempfile

from mailshake import (
    EmailMessage, BaseMailer, DummyMailer, ToMemoryMailer, ToConsoleMailer, ToFileMailer)
from mailshake._compat import StringIO
import pytest


def make_emails():
    return [EmailMessage('Subject',
                         'Content #%s' % content, 'from@example.com',
                         'to@example.com')
            for content in range(1, 5)]


def test_base_mailer():
    mailer = BaseMailer()
    mailer.open()
    mailer.close()
    with pytest.raises(NotImplementedError):
        mailer.send()


def test_dummy_mailer():
    mailer = DummyMailer()
    email1, email2, email3, email4 = make_emails()

    assert mailer.send_messages(email1) == 1
    assert mailer.send_messages(email2, email3, email4) == 3


def test_to_memory_mailer():
    mailer = ToMemoryMailer()
    email1, email2, email3, email4 = make_emails()

    assert mailer.send_messages(email1) == 1
    assert mailer.send_messages(email2, email3, email4) == 3
    assert len(mailer.outbox) == 4
    assert mailer.outbox[1] == email2


def test_to_console_mailer():
    __stdout = sys.stdout
    s = sys.stdout = StringIO()

    mailer = ToConsoleMailer()
    mailer.send('Subject', 'Content', 'from@example.com', 'to@example.com')

    value = s.getvalue()
    assert value.startswith('Content-Type: text/plain; charset="utf-8"'
                            '\nMIME-Version: 1.0'
                            '\nContent-Transfer-Encoding: 7bit'
                            '\nSubject: Subject'
                            '\nFrom: from@example.com'
                            '\nTo: to@example.com'
                            '\nDate: ')
    mailer.send_messages()

    mailer.stream = ''
    with pytest.raises(Exception):
        mailer.send('Subject', 'Content', 'from@example.com', 'to@example.com')
    mailer.fail_silently = True
    mailer.send('Subject', 'Content', 'from@example.com', 'to@example.com')

    sys.stdout = __stdout


def test_to_console_stream_kwarg():
    """Test that the console backend can be pointed at an arbitrary stream.
    """
    s = StringIO()
    mailer = ToConsoleMailer(stream=s)
    mailer.send('Subject', 'Content', 'from@example.com', 'to@example.com')

    value = s.getvalue()
    assert value.startswith('Content-Type: text/plain; charset="utf-8"'
                            '\nMIME-Version: 1.0'
                            '\nContent-Transfer-Encoding: 7bit'
                            '\nSubject: Subject'
                            '\nFrom: from@example.com'
                            '\nTo: to@example.com'
                            '\nDate: ')


def test_to_file_mailer():
    tmp_dir = tempfile.mkdtemp()
    mailer = ToFileMailer(tmp_dir)

    n = mailer.send('Subject', 'Content', 'from@example.com', 'to@example.com')
    assert n == 1
    assert len(os.listdir(tmp_dir)) == 1

    filepath = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])
    message = email.message_from_file(open(filepath))

    assert message.get_content_type() == 'text/plain'
    assert message.get('subject') == 'Subject'
    assert message.get('from') == 'from@example.com'
    assert message.get('to') == 'to@example.com'

    shutil.rmtree(tmp_dir, True)

    mailer = ToFileMailer(__file__)
    assert mailer.path == os.path.dirname(__file__)


def test_to_file_mailer_dir_creation():
    tmp_dir = os.path.join(os.path.dirname(__file__), 'qwertyuiop12345')
    ToFileMailer(tmp_dir)

    assert os.path.isdir(tmp_dir)

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_unique_filename():
    tmp_dir = tempfile.mkdtemp()
    mailer1 = ToFileMailer(tmp_dir)
    mailer2 = ToFileMailer(tmp_dir)
    mailer1.send('Subject', 'Content', 'from@example.com', 'to@example.com')
    mailer2.send('Subject', 'Content', 'from@example.com', 'to@example.com')

    assert len(os.listdir(tmp_dir)) == 2

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_one_file():
    tmp_dir = tempfile.mkdtemp()
    mailer = ToFileMailer(tmp_dir, multifile=False)
    email1, email2, email3, email4 = make_emails()

    assert mailer.send_messages(email1) == 1
    assert mailer.send_messages(email2, email3) == 2
    assert mailer.send_messages(email4) == 1
    assert len(os.listdir(tmp_dir)) == 1

    shutil.rmtree(tmp_dir, True)


def test_to_file_mailer_multifile():
    tmp_dir = tempfile.mkdtemp()
    mailer = ToFileMailer(tmp_dir, multifile=True)
    email1, email2, email3, email4 = make_emails()

    assert mailer.send_messages(email1) == 1
    assert mailer.send_messages(email2, email3) == 2
    assert mailer.send_messages(email4) == 1
    assert len(os.listdir(tmp_dir)) == 3

    shutil.rmtree(tmp_dir, True)
