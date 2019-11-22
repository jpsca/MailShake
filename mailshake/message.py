from pathlib import Path
from email import encoders
from email.message import EmailMessage as PyEmailMessage
from email.headerregistry import Address
from email.mime.base import MIMEBase
from email.utils import formatdate, make_msgid
import mimetypes

import html2text

from .utils import DNS_NAME


textify = html2text.HTML2Text()

# Default MIME type to use on attachments (if it is not explicitly given
# and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = "application/octet-stream"


def to_str(s, encoding="utf-8", errors="strict"):
    """Force a string to be the native text_type
    """
    if issubclass(type(s), str):
        return s
    if isinstance(s, bytes):
        return str(s, encoding, errors)
    return str(s)


def format_addresses_list(values):
    return (format_address(value) for value in values)


def format_address(value):
    if isinstance(value, tuple):
        return Address(*value)
    else:
        return Address(username=value)


class EmailMessage(object):
    """A container for email information.
    """

    def __init__(
        self,
        subject="",
        text="",
        from_email=None,
        to=None,
        *,
        html="",
        cc=None,
        bcc=None,
        reply_to=None,
        attachments=None,
        headers=None,
        encoding="utf-8",
        tags=None,
    ):
        """Initialize a single email message (which can be sent to multiple
        recipients).

        `tags` are ignored unless the mailer supports them (eg. Amazon SES)
        """
        self.subject = subject

        text = to_str(text or "")
        html = to_str(html or "")
        if html and not text:
            text = textify.handle(html)
        self.text = text
        self.html = html

        self.from_email = from_email

        to = to or []
        if not isinstance(to, (list, tuple)):
            self.to = [to]
        else:
            self.to = [to_str(_to) for _to in to]

        cc = cc or []
        if not isinstance(cc, (list, tuple)):
            self.cc = [cc]
        else:
            self.cc = [to_str(_cc) for _cc in cc]

        bcc = bcc or []
        if not isinstance(bcc, (list, tuple)):
            self.bcc = [bcc]
        else:
            self.bcc = [to_str(_bcc) for _bcc in bcc]

        reply_to = reply_to or []
        if not isinstance(reply_to, (list, tuple)):
            self.reply_to = [reply_to]
        else:
            self.reply_to = [to_str(rt) for rt in reply_to]

        self.attachments = []
        if attachments:
            for attachment in attachments:
                self.attach(*attachment)

        self.encoding = encoding
        self.extra_headers = headers or {}
        self.tags = tags

    def get_recipients(self):
        """Returns a list of all recipients of the email (includes direct
        addressees as well as Cc and Bcc entries).
        """
        return [email for email in (self.to + self.cc + self.bcc) if email]

    def attach(self, filename, content, mimetype=None):
        """
        Attach a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.
        If the first parameter is a MIMEBase subclass, insert it directly
        into the resulting message attachments.

        For a text/* mimetype (guessed or specified), when a bytes object is
        specified as content, decode it as UTF-8. If that fails, set the
        mimetype to DEFAULT_ATTACHMENT_MIME_TYPE and don't decode the content.
        """
        mimetype = (
            mimetype
            or mimetypes.guess_type(filename)[0]
            or DEFAULT_ATTACHMENT_MIME_TYPE
        )
        maintype, subtype = mimetype.split("/", 1)

        if maintype == "text":
            if isinstance(content, bytes):
                try:
                    content = content.decode()
                except UnicodeDecodeError:
                    # If mimetype suggests the file is text but it's
                    # actually binary, read() raises a UnicodeDecodeError.
                    maintype, subtype = DEFAULT_ATTACHMENT_MIME_TYPE.split("/", 1)

        self.attachments.append((filename, maintype, subtype, content))

    def attach_file(self, path, mimetype=None):
        """
        Attach a file from the filesystem.
        Set the mimetype to DEFAULT_ATTACHMENT_MIME_TYPE if it isn't specified
        and cannot be guessed.
        For a text/* mimetype (guessed or specified), decode the file's content
        as UTF-8. If that fails, set the mimetype to
        DEFAULT_ATTACHMENT_MIME_TYPE and don't decode the content.
        """
        path = Path(path)
        self.attach(path.name, path.read_bytes(), mimetype)

    def render(self, with_attachments=True):
        msg = PyEmailMessage()
        msg.encoding = self.encoding
        msg.set_content(self.text)
        if self.html:
            msg.add_alternative(self.html, subtype="html")
        if self.attachments:
            msg.make_mixed()

        msg["Subject"] = self.subject
        msg["From"] = format_address(self.from_email)
        msg["To"] = format_addresses_list(self.to)
        msg["Cc"] = format_addresses_list(self.cc)
        msg["Reply-To"] = format_addresses_list(self.reply_to)

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]

        if "date" not in header_names:
            msg["Date"] = formatdate(localtime=True)

        if "message-id" not in header_names:
            # Use cached DNS_NAME for performance
            msg["Message-ID"] = make_msgid(domain=DNS_NAME)

        for name, value in self.extra_headers.items():
            msg[name] = value

        if with_attachments:
            for filename, maintype, subtype, content in self.attachments:
                attachment = MIMEBase(maintype, subtype)
                attachment.set_payload(content)
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"'
                )
                msg.attach(attachment)
        return msg

    def as_string(self, with_attachments=False, unixfrom=False):
        return self.render(with_attachments).as_string(unixfrom)

    def as_bytes(self, with_attachments=False, unixfrom=False):
        return self.render(with_attachments).as_bytes(unixfrom)
