# MailShake
    
Although Python makes sending email relatively easy via the smtplib module, this bundle provides a couple of light wrappers over it.

These wrappers are provided to make sending email extra quick, to make it easy to test email sending during development, and to provide support for platforms that can’t use SMTP.

Usage:

    from mailshake import EmailMessage, Mailer
    
    email_msg = EmailMessage(
        "Weekend getaway",
        'Here's a photo of us from our Europe trip.',
        'from@example.com',
        ['mary@example.com', 'bob@example.com'],
        
        )
    email_msg.attach("picture.jpg")
    
    mailer = Mailer()
    mailer.send(email_msg)

Severals other mailers are available for testing: `ToConsoleMailer`, `ToFileMailer`, `ToMemoryMailer` and `DummyMailer` (does nothing).

.

--------

Much of the code was based on the mail backends of Django (http://djangoproject.com).<br>
The original code was BSD licensed. See `LEGAL.md` for more details.

Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).<br>
MIT License. (http://www.opensource.org/licenses/mit-license.php)
