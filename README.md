![Mailshake logo](https://raw.github.com/jpsca/mailshake/master/docs/static/images/mailshake@2x.png)

# Mailshake

[![Build Status](https://travis-ci.org/jpsca/mailshake.svg?branch=master)](https://travis-ci.org/jpsca/mailshake)

Although Python makes sending email relatively easy via the smtplib
module, this library provides a couple of light wrappers over it.

These wrappers make sending email extra quick, easy to test email
sending during development, and provides support for platforms that
can't use SMTP.

Mailers availiable:

-   SMTPMailer
-   AmazonSESMailer
-   ToConsoleMailer (prints the emails in the console)
-   ToFileMailer (save the emails in a file)
-   ToMemoryMailer (for testing)
-   DummyMailer (does nothing)

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

## Install for development

First, create an activate a virtualenv. eg:

```bash
python -m virtualenv .venv
source .venv/bin/activate
```

Then run `pip install -e .[dev]` or `make install`. This will install the library in editable mode and all its dependencies.
