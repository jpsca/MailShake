# -*- coding: utf-8 -*-
"""
=================
MailShake
=================

Although Python makes sending email relatively easy via the smtplib module, this library provides a couple of light wrappers over it.

These wrappers are provided to make sending email extra quick, to make it easy to test email sending during development, and to provide support for platforms that can’t use SMTP.

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

--------
[MIT License](http://www.opensource.org/licenses/mit-license.php).

© 2011 by [Lúcuma labs](http://lucumalabs.com).

"""
from .mailers.base import BaseMailer
from .mailers.console import ToConsoleMailer
from .mailers.dummy import DummyMailer
from .mailers.filebased import ToFileMailer
from .mailers.memory import ToMemoryMailer
from .mailers.smtp import SMTPMailer

from .mailers.amazon_ses import AmazonSESMailer

from .message import EmailMessage


Mailer = ToConsoleMailer

__version__ = '0.9.7'
