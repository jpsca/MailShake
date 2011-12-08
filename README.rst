
=================
MailShake
=================

Although Python makes sending email relatively easy via the smtplib module,
this bundle provides a couple of light wrappers over it.

These wrappers are provided to make sending email extra quick, to make it
easy to test email sending during development, and to provide support for
platforms that can’t use SMTP.

Usage::

    from mailshake import EmailMessage, SMTPMailer
    
    email_msg = EmailMessage(
        "Weekend getaway",
        'Here's a photo of us from our Europe trip.',
        'from@example.com',
        ['mary@example.com', 'bob@example.com'],
        
        )
    email_msg.attach("picture.jpg")
    
    mailer = SMTPMailer()
    mailer.send(email_msg)


Severals other mailers are available for testing: `ToConsoleMailer`,
`DummyMailer` (does nothing), `ToFileMailer` and `ToMemoryMailer`.


