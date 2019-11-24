![Mailshake logo](https://raw.github.com/jpscaletti/mailshake/master/docs/static/images/mailshake@2x.png)

# Mailshake

[![Build Status](https://travis-ci.org/jpscaletti/MailShake.svg?branch=master)](https://travis-ci.org/jpscaletti/MailShake)

Although Python makes sending email relatively easy via the smtplib
module, this library provides a couple of light wrappers over it.

These wrappers make sending email extra quick, easy to test email
sending during development, and provides support for platforms that
can't use SMTP.

*Compatible with Python 3.6+*

Mailers availiable:

-   SMTPMailer
-   AmazonSESMailer
-   ToConsoleMailer (prints the emails in the console)
-   ToMemoryMailer (for testing)

Usage:

```python
from mailshake import SMTPMailer

mailer = SMTPMailer()
mailer.send(
    subject='Hi',
    text_content='Hello world!',
    from_email='from@example.com',
    to=['mary@example.com', 'bob@example.com']
)
```

You can also compose several messages and send them at the same time:

```python
from mailshake import SMTPMailer, EmailMessage

mailer = SMTPMailer()
messages = []

email_msg = EmailMessage(
    "Weekend getaway",
    "Here's a photo of us from our trip.",
    "from@example.com",
    "bob@example.com"
)
email_msg.attach_file("picture.jpg")
messages.append(email_msg)

#…

mailer.send_messages(*messages)
```
