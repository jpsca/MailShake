# -*- coding: utf-8 -*-
"""
    # mailshake.message

    A container for email information.

"""
from email import charset as Charset, encoders as Encoders
from email.generator import Generator
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email.utils import formatdate, getaddresses, parseaddr
import mimetypes
import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .utils import (DNS_NAME, sanitize_address, make_msgid,
    to_unicode, to_bytestring)


# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
Charset.add_charset('utf-8', Charset.SHORTEST, None, 'utf-8')

# Default MIME type to use on attachments (if it is not explicitly given
# and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = 'application/octet-stream'

# Header names that contain structured address data (RFC #5322)
ADDRESS_HEADERS = set([
    'from',
    'sender',
    'reply-to',
    'to',
    'cc',
    'bcc',
    'resent-from',
    'resent-sender',
    'resent-to',
    'resent-cc',
    'resent-bcc',
])


class EmailMessage(object):
    """A container for email information.
    """
    content_subtype = 'plain'
    mixed_subtype = 'mixed'
    html_subtype = 'html'
    alternative_subtype = 'alternative'
    encoding = 'utf-8'

    def __init__(self, subject='', text_content='', from_email=None, to=None, 
            cc=None, bcc=None, html_content=None, attachments=None,
            headers=None):
        """Initialize a single email message (which can be sent to multiple
        recipients).

        All strings used to create the message can be unicode strings
        (or UTF-8 bytestrings). The SafeMIMEText class will handle any
        necessary encoding conversions.
        """
        to = to or []
        if isinstance(to, basestring):
            to = [to]
        self.to = list(to)
        
        cc = cc or []
        if isinstance(cc, basestring):
            cc = [cc]
        self.cc = list(cc)
        
        bcc = bcc or []
        if isinstance(bcc, basestring):
            bcc = [bcc]
        self.bcc = list(bcc)

        self.from_email = from_email
        self.subject = subject
        self.text_content = text_content
        self.html_content = html_content
        self.attachments = attachments or []
        self.extra_headers = headers or {}

    def message(self):
        msg = self._create_message()
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = ', '.join(self.to)
        if self.cc:
            msg['Cc'] = ', '.join(self.cc)
        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            msg['Message-ID'] = make_msgid()
        for name, value in self.extra_headers.items():
            if name.lower() == 'from':  # From is already handled
                continue
            msg[name] = value
        return msg
    
    def as_string(self, unixfrom=False):
        return self.message().as_string(unixfrom)

    def get_recipients(self):
        """Returns a list of all recipients of the email (includes direct
        addressees as well as Cc and Bcc entries).
        """
        return self.to + self.cc + self.bcc
    
    def attach(self, filename=None, content=None, mimetype=None):
        """Attaches a file with the given filename and content. The filename
        can be omitted and the mimetype is guessed, if not provided.

        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        """
        if isinstance(filename, MIMEBase):
            assert content == mimetype == None
            self.attachments.append(filename)
        else:
            assert content is not None
            self.attachments.append((filename, content, mimetype))

    def attach_file(self, path, mimetype=None):
        """Attaches a file from the filesystem.
        """
        filename = os.path.basename(path)
        content = open(path, 'rb').read()
        self.attach(filename, content, mimetype)

    def _create_message(self):
        text_content = ''
        if self.text_content:
            text_content = SafeMIMEText(to_bytestring(self.text_content,
                self.encoding), self.content_subtype, self.encoding)
        msg = text_content
        
        if self.html_content:
            msg = SafeMIMEMultipart(_subtype=self.alternative_subtype,
                encoding=self.encoding)
            if text_content:
                msg.attach(text_content)
            
            if self.html_content:
                html_content = SafeMIMEText(to_bytestring(self.html_content,
                    self.encoding), self.html_subtype, self.encoding)
                msg.attach(html_content)
        
        if self.attachments:
            _msg = SafeMIMEMultipart(_subtype=self.mixed_subtype,
                encoding=self.encoding)
            _msg.attach(msg)
            msg = _msg
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_attachment(*attachment))
        
        return msg

    def _create_attachment(self, filename, content, mimetype=None):
        """Converts the filename, content, mimetype triple into a
        MIME attachment object.
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        attachment = self._create_mime_attachment(content, mimetype)
        if filename:
            attachment.add_header('Content-Disposition', 'attachment',
                filename=filename)
        return attachment
    
    def _create_mime_attachment(self, content, mimetype):
        """Converts the content, mimetype pair into a MIME attachment object.
        """
        basetype, subtype = mimetype.split('/', 1)
        if basetype == 'text':
            attachment = SafeMIMEText(to_bytestring(content, self.encoding),
                subtype, self.encoding)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            Encoders.encode_base64(attachment)
        return attachment


class SafeMIMEText(MIMEText):

    def __init__(self, text, subtype, charset):
        self.encoding = charset
        MIMEText.__init__(self, text, subtype, charset)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEText.__setitem__(self, name, val)

    def as_string(self, unixfrom=False):
        """Return the entire formatted message as a string.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.

        This overrides the default as_string() implementation to not mangle
        lines that begin with 'From '. See bug #13433 for details.
        """
        fp = StringIO()
        g = Generator(fp, mangle_from_ = False)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()


class SafeMIMEMultipart(MIMEMultipart):

    def __init__(self, _subtype='mixed', boundary=None, _subparts=None,
            encoding=None, **_params):
        self.encoding = encoding
        MIMEMultipart.__init__(self, _subtype, boundary, _subparts, **_params)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEMultipart.__setitem__(self, name, val)

    def as_string(self, unixfrom=False):
        """Return the entire formatted message as a string.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.

        This overrides the default as_string() implementation to not mangle
        lines that begin with 'From '. See bug #13433 for details.
        """
        fp = StringIO()
        g = Generator(fp, mangle_from_ = False)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()


def forbid_multi_line_headers(name, val, encoding='utf-8'):
    """Forbids multi-line headers, to prevent header injection.
    """
    val = to_unicode(val)
    if '\n' in val or '\r' in val:
        raise ValueError("Header values can't contain newlines' \
            ' (got %r for header %r)" % (val, name))
    try:
        val = val.encode('ascii')
    except UnicodeEncodeError:
        if name.lower() in ADDRESS_HEADERS:
            val = ', '.join(sanitize_address(addr, encoding)
                for addr in getaddresses((val,)))
        else:
            val = str(Header(val, encoding))
    else:
        if name.lower() == 'subject':
            val = Header(val)
    return name, val

