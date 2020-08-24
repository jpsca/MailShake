import email
from email import message_from_string
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.message import MIMEMessage
import email.policy
from email.utils import formatdate, getaddresses
import mimetypes
import os

import html2text

from .utils import encode_address, forbid_multi_line_headers, make_msgid, to_str


textify = html2text.HTML2Text()

# Header names that contain structured address data (RFC #5322)
ADDRESS_HEADERS = set(
    [
        "from",
        "sender",
        "reply-to",
        "to",
        "cc",
        "bcc",
        "resent-from",
        "resent-sender",
        "resent-to",
        "resent-cc",
        "resent-bcc",
    ]
)

# Don't BASE64-encode UTF-8 messages
utf8_charset = email.charset.Charset("utf-8")
utf8_charset.body_encoding = None  # Python defaults to BASE64
email.charset.add_charset("utf-8", email.charset.SHORTEST, None, "utf-8")

# Default MIME type to use on attachments (if it is not explicitly given
# and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = "application/octet-stream"


class SafeMIMEMixin:
    encoding = "ascii"

    def __init__(self, *args, **kw):
        self.charset = email.charset.Charset(self.encoding)
        super().__init__(*args, **kw)

    def __setitem__(self, name, val):
        name, val = to_str(name, self.encoding), to_str(val, self.encoding)
        forbid_multi_line_headers(name, val)
        try:
            val.encode("ascii")
        except UnicodeEncodeError:
            if name.lower() in ADDRESS_HEADERS:
                val = ", ".join(
                    encode_address(addr, self.charset) for addr in getaddresses((val,))
                )
            else:
                val = self.charset.header_encode(val)
        MIMEMessage.__setitem__(self, name, val)


class SafeMIMEMessage(SafeMIMEMixin, MIMEMessage):
    pass


class SafeMIMEText(SafeMIMEMixin, MIMEText):
    def __init__(self, text, subtype, charset):
        self.encoding = charset
        super().__init__(text, subtype, charset)


class SafeMIMEMultipart(SafeMIMEMixin, MIMEMultipart):
    def __init__(
        self, _subtype="mixed", boundary=None, _subparts=None, encoding=None, **_params
    ):
        self.encoding = encoding
        super().__init__(_subtype, boundary, _subparts, **_params)


class EmailMessage:

    """A container for email information.
    """

    content_subtype = "plain"
    mixed_subtype = "mixed"
    html_subtype = "html"
    alternative_subtype = "alternative"

    def __init__(
        self,
        subject="",
        text="",
        from_email=None,
        to=None,
        cc=None,
        bcc=None,
        reply_to=None,
        html=None,
        attachments=None,
        headers=None,
        text_content=None,
        html_content=None,
        encoding="utf-8",
        tags=None,
    ):
        """Initialize a single email message (which can be sent to multiple
        recipients).

        All strings used to create the message can be unicode strings
        (or UTF-8 bytestrings). The SafeMIMEText class will handle any
        necessary encoding conversions.

        `text_content` and `html_content` parameters exists for backwards
        compatibility. Use `text` and `html` instead.

        `tags` are ignored unless the mailer supports them (eg. Amazon SES)
        """
        self.encoding = encoding
        to = to or []
        if isinstance(to, str):
            to = [to]
        self.to = [encode_address(addr, self.encoding) for addr in to]
        cc = cc or []
        if isinstance(cc, str):
            cc = [cc]
        self.cc = [encode_address(addr, self.encoding) for addr in cc]

        bcc = bcc or []
        if isinstance(bcc, str):
            bcc = [bcc]
        self.bcc = [encode_address(addr, self.encoding) for addr in bcc]

        reply_to = reply_to or []
        if isinstance(reply_to, str):
            reply_to = [reply_to]
        self.reply_to = [encode_address(addr, self.encoding) for addr in reply_to]

        self.from_email = from_email
        self.subject = subject
        self.attachments = attachments or []
        self.extra_headers = headers or {}

        text = to_str(text or text_content or "")
        html = to_str(html or html_content or "")
        if html and not text:
            text = textify.handle(html)
        self.text = text
        self.html = html
        self.tags = tags

    def render(self):
        msg = self._create_message()
        msg["Subject"] = self.subject
        msg["From"] = self.extra_headers.get("From", self.from_email)

        if self.to:
            msg["To"] = ", ".join(self.to)

        if self.cc:
            msg["Cc"] = ", ".join(self.cc)

        if self.reply_to:
            msg["Reply-To"] = ", ".join(self.reply_to)

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if "date" not in header_names:
            msg["Date"] = formatdate()

        if "message-id" not in header_names:
            msg["Message-ID"] = make_msgid()

        for name, value in self.extra_headers.items():
            if name.lower() in ("from", "to"):  # From and To are already handled
                continue
            msg[name] = value

        return msg

    def as_string(self, unixfrom=False):
        return self.render().as_string(unixfrom, policy=email.policy.default)

    def as_bytes(self, unixfrom=False):
        return self.render().as_bytes(unixfrom, policy=email.policy.default)

    def get_recipients(self):
        """Returns a list of all recipients of the email (includes direct
        addressees as well as Cc and Bcc entries).
        """
        return self.to + self.cc + self.bcc

    def attach(self, filename=None, content=None, mimetype=None):
        """
        Attaches a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.
        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        """
        if isinstance(filename, MIMEBase):
            assert content is None
            assert mimetype is None
            self.attachments.append(filename)
        else:
            assert content is not None
            self.attachments.append((filename, content, mimetype))

    def attach_file(self, path, mimetype=None):
        """Attaches a file from the filesystem."""
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            content = f.read()
        self.attach(filename, content, mimetype)

    def _create_message(self):
        text = SafeMIMEText(
            to_str(self.text or ""), self.content_subtype, self.encoding
        )
        msg = text

        if self.html:
            msg = SafeMIMEMultipart(
                _subtype=self.alternative_subtype, encoding=self.encoding
            )
            if self.text:
                msg.attach(text)

            if self.html:
                html = SafeMIMEText(
                    to_str(self.html or "").encode(self.encoding),
                    self.html_subtype,
                    self.encoding,
                )
                msg.attach(html)

        if self.attachments:
            _msg = SafeMIMEMultipart(
                _subtype=self.mixed_subtype, encoding=self.encoding
            )
            _msg.attach(msg)
            msg = _msg
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_attachment(*attachment))

        return msg

    def _create_attachment(self, filename, content, mimetype=None):
        """
        Converts the filename, content, mimetype triple into a MIME attachment
        object.
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        attachment = self._create_mime_attachment(content, mimetype)
        if filename:
            try:
                filename.encode("ascii")
            except UnicodeEncodeError:
                filename = ("utf-8", "", filename)
            attachment.add_header(
                "Content-Disposition", "attachment", filename=filename
            )
        return attachment

    def _create_mime_attachment(self, content, mimetype):
        """
        Converts the content, mimetype pair into a MIME attachment object.
        If the mimetype is message/rfc822, content may be an
        email.Message or EmailMessage object, as well as a str.
        """
        basetype, subtype = mimetype.split("/", 1)
        if basetype == "text":
            encoding = self.encoding
            attachment = SafeMIMEText(content, subtype, encoding)
        elif basetype == "message" and subtype == "rfc822":
            # Bug #18967: per RFC2046 s5.2.1, message/rfc822 attachments
            # must not be base64 encoded.
            if isinstance(content, EmailMessage):
                # convert content into an email.Message first
                content = content.message()
            elif not isinstance(content, Message):
                # For compatibility with existing code, parse the message
                # into an email.Message object if it is not one already.
                content = message_from_string(content)

            attachment = SafeMIMEMessage(content, subtype)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            email.encoders.encode_base64(attachment)
        return attachment
