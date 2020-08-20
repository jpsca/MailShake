"""
Adapted from Django (http://djangoproject.com).
The original code was BSD licensed (see LICENSE)
"""
from email.charset import Charset
from email.header import Header
from email.utils import formataddr, getaddresses, parseaddr
import os
import random
import socket
import time
import warnings


class CachedDnsName(object):
    """Cache the hostname, but do it lazily: socket.getfqdn() can take a
    couple of seconds, which slows down the restart of the server.
    """

    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, "_fqdn"):
            self._fqdn = socket.getfqdn()
        return self._fqdn


DNS_NAME = CachedDnsName()


def split_addr(addr, encoding):
    warnings.warn(
        "the split_addr function is deprecated, you can use a simple "
        "`.rsplit('@', 1)` instead", DeprecationWarning
    )
    return encode_address(addr, encoding).rsplit("@", 1)


def encode_address(addr, charset):
    """Encode a pair of (name, address) or an email address string.

    When non-ascii characters are present in the name or local part, they're
    MIME-word encoded. The domain name is idna-encoded if it contains
    non-ascii characters.
    """
    if not isinstance(addr, tuple):
        addr = parseaddr(to_str(addr))
    name, addr = addr
    if isinstance(charset, str):
        charset = Charset(charset)
    if "@" in addr:
        localpart, domain = addr.rsplit("@", 1)
        # Try to get the simplest encoding - ascii if possible so that
        # to@example.com doesn't become =?utf-8?q?to?=@example.com. This
        # makes unit testing a bit easier and more readable.
        try:
            localpart.encode("ascii")
        except UnicodeEncodeError:
            localpart = charset.header_encode(localpart)
        addr = localpart + "@" + domain.encode("idna").decode("ascii")
        del localpart, domain
    else:
        try:
            addr.encode("ascii")
        except UnicodeEncodeError:
            addr = charset.header_encode(addr)
    return formataddr((name, addr), charset=charset)


def sanitize_address(addr, encoding):
    warnings.warn(
        "the sanitize_address function has been replaced by encode_address",
        DeprecationWarning
    )
    return encode_address(addr, encoding)


def make_msgid(idstring=None):
    """Returns a string suitable for RFC 2822 compliant Message-ID, e.g:

    <20020201195627.33539.96671@nightshade.la.mastaler.com>

    Optional idstring if given is a string used to strengthen the
    uniqueness of the message id.
    """
    timeval = time.time()
    utcdate = time.strftime("%Y%m%d%H%M%S", time.gmtime(timeval))
    try:
        pid = os.getpid()
    except AttributeError:
        pid = 1
    randint = random.randrange(100000)
    if idstring is None:
        idstring = ""
    else:
        idstring = "." + idstring
    idhost = DNS_NAME
    msgid = "<{}.{}.{}{}@{}>".format(utcdate, pid, randint, idstring, idhost)
    return msgid


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


def forbid_multi_line_headers(name, val, encoding="utf-8"):
    """Forbids multi-line headers, to prevent header injection.
    """
    val = to_str(val)
    if "\n" in val or "\r" in val:
        raise ValueError(
            "Header values can't contain newlines "
            "(got {val} for header {name})".format(val=val, name=name)
        )
    try:
        val.encode("ascii")
    except UnicodeEncodeError:
        if name.lower() in ADDRESS_HEADERS:
            val = ", ".join(
                [encode_address(addr, encoding) for addr in getaddresses((val,))]
            )
        else:
            val = Header(val, encoding).encode()
    else:
        if name.lower() == "subject":
            val = Header(val).encode()
    return str(name), val


def to_str(s, encoding="utf-8", errors="strict"):
    """Force a string to be the native text_type
    """
    if isinstance(s, str):
        return s

    if isinstance(s, str):
        return s.decode(encoding, errors)

    if isinstance(s, bytes):
        return str(s, encoding, errors)

    return str(s)
