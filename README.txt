
Shake-Mail
----------------------------------------------

Simple front end to the smtplib and email modules, to simplify sending
email from your Shake app.

Usage:
    
    import shake_mail
    
    message = shake_mail.Message(
        From = "me@example.com",
        To = "you@example.com",
        Subject = "My Vacation",
        )
    message.Body = open("letter.txt", "rb").read()
    message.attach("picture.jpg")
    
    mailer = shake_mail.Mailer('mail.example.com')
    mailer.send(message)


Adapted from the mailer module by Ryan Ginstrom
http://pypi.python.org/pypi/mailer/0.5
Used under the MIT license

:Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
:MIT License. (http://www.opensource.org/licenses/mit-license.php)
