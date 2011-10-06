# -*- coding: utf-8 -*-
"""
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

"""
from email import encoders
from email.header import make_header
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes    # For guessing MIME type based on file name extension
import os
import smtplib


class Message(object):
    """Represents an email message.
    
    Set the To, From, Subject, and Body attributes as plain-text strings.
    Optionally, set the Html attribute to send an HTML email, or use the
    attach() method to attach files.
    
    Use the charset property to send messages using other than us-ascii
    
    If you specify an attachments argument, it should be a list of
    attachment filenames: ["file1.txt", "file2.txt"]
    
    `To` should be a string for a single address, and a sequence
    of strings for multiple recipients (castable to list)
    
    Send using the Mailer class.
    
    """
    
    def __init__(self, To=None, From=None, Subject=None, Body=None, Html=None,
          attachments=None, charset='utf-8'):
        self.attachments = []
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, basestring):
                    self.attachments.append((attachment, None))
                else:
                    try:
                        filename, cid = attachment
                    except (TypeError, IndexError):
                        self.attachments.append((attachment, None))
                    else:
                        self.attachments.append((filename, cid))
        
        self.To = To
        """string or iterable"""
        self.From = From
        """string"""
        self.Subject = Subject
        self.Body = Body
        self.Html = Html
        self.charset = charset
    
    def as_string(self):
        """Get the email as a string to send in the mailer.
        """
        if not self.attachments:
            return self._plaintext()
        else:
            return self._multipart()
    
    def _plaintext(self):
        """Plain text email with no attachments.
        """
        if isinstance(self.Body, unicode):
            self.Body = self.Body.encode(self.charset)
        
        if not self.Html:
            msg = MIMEText(self.Body, 'plain', self.charset)
        else:
            if isinstance(self.Html, unicode):
                self.Html = self.Html.encode(self.charset)
            msg = self._with_html()
        
        self._set_info(msg)
        return msg.as_string()
    
    def _with_html(self):
        """There's an html part.
        """
        outer = MIMEMultipart('alternative')
        
        part1 = MIMEText(self.Body, 'plain', self.charset)
        part2 = MIMEText(self.Html, 'html', self.charset)
        
        outer.attach(part1)
        outer.attach(part2)
        
        return outer
    
    def _set_info(self, msg):
        if self.charset == 'us-ascii':
            msg['Subject'] = self.Subject
        else:
            subject = unicode(self.Subject, self.charset)
            msg['Subject'] = str(make_header([(subject, self.charset)]))
        msg['From'] = self.From
        if isinstance(self.To, basestring):
            msg['To'] = self.To
        else:
            self.To = list(self.To)
            msg['To'] = ", ".join(self.To)
    
    def _multipart(self):
        """The email has attachments.
        """
        msg = MIMEMultipart('related')
        
        if isinstance(self.Body, unicode):
            self.Body = self.Body.encode(self.charset)
        
        if self.Html:
            if isinstance(self.Html, unicode):
                self.Html = self.Html.encode(self.charset)
            
            outer = MIMEMultipart('alternative')
            
            part1 = MIMEText(self.Body, 'plain', self.charset)
            part1.add_header('Content-Disposition', 'inline')
            
            part2 = MIMEText(self.Html, 'html', self.charset)
            part2.add_header('Content-Disposition', 'inline')
            
            outer.attach(part1)
            outer.attach(part2)
            msg.attach(outer)
        else:
            msg.attach(MIMEText(self.Body, 'plain', self.charset))
        
        self._set_info(msg)
        msg.preamble = self.Subject
        
        for filename, cid in self.attachments:
            self._add_attachment(msg, filename, cid)
        
        return msg.as_string()
    
    def _add_attachment(self, outer, filename, cid):
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        fp = open(filename, 'rb')
        if maintype == 'text':
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        fp.close()
        
        # Set the content-ID header
        if cid:
            msg.add_header('Content-ID', '<%s>' % cid)
            msg.add_header('Content-Disposition', 'inline')
        else:
            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment',
                filename=os.path.basename(filename))
        outer.attach(msg)
    
    def attach(self, filename, cid=None):
        """Attach a file to the email. Specify the name of the file;
        Message will figure out the MIME type and load the file.
        """
        self.attachments.append((filename, cid))


class Mailer(object):
    """Represents an SMTP connection.
    
    Use sign_in() to sign in with a username and password.
    """
    
    def __init__(self, host="localhost", port=25, user=None,
          password=None, tls=True, default_from=None):
        self.host = host
        self.port = port
        self._usr = user
        self._pwd = password
        self.tls = tls
        default_from = default_from or user or 'webmaster'
        if '@' not in default_from:
            default_from += '@' + host
        self.default_from = default_from
    
    def sign_in(self, user, password):
        self._usr = user
        self._pwd = password
    
    def send(self, msg):
        """Send one message or a sequence of messages.
        
        Every time you call send, the mailer creates a new connection,
        so if you have several emails to send, pass them as a list:
        mailer.send([msg1, msg2, msg3])
        """
        server = smtplib.SMTP(self.host, self.port)
        if self.tls:
            server.ehlo()
            server.starttls()
            server.ehlo()
        
        if self._usr and self._pwd:
            server.login(self._usr, self._pwd)
        
        if hasattr(msg, '__iter__'):
            for m in msg:
                self._send(server, m)
        else:
            self._send(server, msg)
        
        server.quit()
    
    def _send(self, server, msg):
        """Sends a single message using the server
        we created in send().
        """
        me = msg.From
        if isinstance(msg.To, basestring):
            you = [msg.To]
        else:
            you = list(msg.To)
        server.sendmail(me, you, msg.as_string())


class ToFileMailer(object):
    """The file mailer writes e-mails to a file.
    
    A new file is created for each call. The directory to which the files are
    written is taken from the ``path`` keyword argument.
    
    This mailer is not intended for use in production -- it is provided as a
    convenience that can be used during development.
    """
    pass


class ToConsoleMailer(object):
    """Instead of sending out real e-mails the console mailer just writes the
    e-mails that would be send to the standard output.
    
    By default, this mailer writes to stdout. You can use a different
    stream-like object by providing the ``stream`` keyword argument when
    instantiate this class.
    
    This mailer is not intended for use in production -- it is provided as a
    convenience that can be used during development.
    """
    pass


class DummyMailer(object):
    """As the name suggests the dummy mailer does nothing with your messages.
    
    This mailer is not intended for use in production -- it is provided as a
    convenience that can be used during development.
    """
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def send(self, msg):
        pass
