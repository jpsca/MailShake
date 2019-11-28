![Mailshake logo](https://raw.github.com/jpscaletti/mailshake/master/docs/static/images/mailshake.png)

[![Build Status](https://travis-ci.org/jpscaletti/MailShake.svg?branch=master)](https://travis-ci.org/jpscaletti/MailShake)

> Documentation: https://mailshake.jpscaletti.com

Sending emails with Python 3 is a little easier than before, but still a mess. 

This library makes it way easier to send emails, test the
sending during development, and provides support for platforms that
don't use SMTP like Amazon SES.

Mailers available:

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
