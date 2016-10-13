# coding=utf-8
"""
=================
MailShake
=================

Although Python makes sending email relatively easy via the smtplib module,
this library provides a couple of light wrappers over it.

Did you know SMTP has a limit of 1000 recipients per email? This library does ;)

These wrappers make sending email extra quick, easy to test email sending during
development, and provides support for platforms that can’t use SMTP.

Usage::

    from mailshake import SMTPMailer

    mailer = SMTPMailer()
    mailer.send(
        subject='Hi',
        text_content='Hello world!',
        from_email='from@example.com',
        to=['mary@example.com', 'bob@example.com']
    )

You can also compose several messages and send them at the same time::

    from mailshake import SMTPMailer, EmailMessage

    mailer = SMTPMailer()
    messages = []
    email_msg = EmailMessage(
        "Weekend getaway",
        'Here's a photo of us from our trip.',
        'from@example.com',
        ['mary@example.com', 'bob@example.com']
    )
    email_msg.attach("picture.jpg")
    messages.append(email_msg)

    …

    mailer.send_messages(messages)


Mailers availiable:
    * SMTPMailer
    * AmazonSESMailer

and:

    * ToConsoleMailer (prints the emails in the console)
    * ToFileMailer (save the emails in a file)
    * ToMemoryMailer (for testing)
    * DummyMailer (does nothing)


:copyright: `Juan-Pablo Scaletti <http://jpscaletti.com>`_.
:license: MIT, see LICENSE for more details.

"""
from .mailers.base import BaseMailer  # noqa
from .mailers.console import ToConsoleMailer  # noqa
from .mailers.dummy import DummyMailer  # noqa
from .mailers.filebased import ToFileMailer  # noqa
from .mailers.memory import ToMemoryMailer  # noqa
from .mailers.smtp import SMTPMailer  # noqa
from .mailers.amazon_ses import AmazonSESMailer  # noqa
from .message import EmailMessage  # noqa


Mailer = ToConsoleMailer

__version__ = '0.14.0'
