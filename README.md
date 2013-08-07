# MailShake

[![Build Status](https://travis-ci.org/lucuma/MailShake.png)](https://travis-ci.org/lucuma/MailShake)
    
Although Python makes sending email relatively easy via the smtplib module, this library provides a couple of light wrappers over it.

These wrappers are provided to make sending email extra quick, to make it easy to test email sending during development, and to provide support for platforms that can’t use SMTP.

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

You can also compose several messages and send them at the same time::

```python
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

#…

mailer.send_messages(messages)
```

--------

© by Lúcuma labs (http://lucumalabs.com).

MIT License. (http://www.opensource.org/licenses/mit-license.php).
Originally derived from the mail backends of Django (http://djangoproject.com). See `LICENSE.md
