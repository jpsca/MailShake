"""
Adapted from Django (http://djangoproject.com).
The original code was BSD licensed (see LICENSE)
"""
from email.header import Header
from email.utils import parseaddr, getaddresses
import os
import random
import socket
import time


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
    """
    Split the address into local part and domain, properly encoded.

    When non-ascii characters are present in the local part, it must be
    MIME-word encoded. The domain name must be idna-encoded if it contains
    non-ascii characters.
    """
    if "@" in addr:
        localpart, domain = addr.split("@", 1)
        # Try to get the simplest encoding - ascii if possible so that
        # to@example.com doesn't become =?utf-8?q?to?=@example.com. This
        # makes unit testing a bit easier and more readable.
        try:
            localpart.encode("ascii")
        except UnicodeEncodeError:
            localpart = Header(localpart, encoding).encode()
        domain = domain.encode("idna").decode("ascii")
    else:
        localpart = Header(addr, encoding).encode()
        domain = ""
    return (localpart, domain)


def sanitize_address(addr, encoding):
    """
    Format a pair of (name, address) or an email address string.
    """
    if not isinstance(addr, tuple):
        addr = parseaddr(to_str(addr))
    nm, addr = addr
    localpart, domain = None, None
    nm = Header(nm, encoding).encode()
    try:
        addr.encode("ascii")
    except UnicodeEncodeError:  # IDN or non-ascii in the local part
        localpart, domain = split_addr(addr, encoding)

    # On Python 3, an `email.headerregistry.Address` object is used since
    # email.utils.formataddr() naively encodes the name as ascii (see #25986).
    from email.headerregistry import Address
    from email.errors import InvalidHeaderDefect, NonASCIILocalPartDefect

    if localpart and domain:
        address = Address(nm, username=localpart, domain=domain)
        return str(address)

    try:
        address = Address(nm, addr_spec=addr)
    except (InvalidHeaderDefect, NonASCIILocalPartDefect):
        localpart, domain = split_addr(addr, encoding)
        address = Address(nm, username=localpart, domain=domain)
    return str(address)


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
    msgid = "<{}.{}.{}@{}>".format(utcdate, pid, randint, idstring, idhost)
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
                [sanitize_address(addr, encoding) for addr in getaddresses((val,))]
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
