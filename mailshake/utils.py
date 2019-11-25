from email.header import Header
from email.utils import parseaddr
from email.headerregistry import Address
from email.errors import InvalidHeaderDefect, NonASCIILocalPartDefect
import socket


def to_str(s, encoding="utf-8", errors="strict"):
    """Force a string to be the native text_type
    """
    if issubclass(type(s), str):
        return s
    if isinstance(s, bytes):
        return str(s, encoding, errors)
    return str(s)


def punycode(domain):
    """Return the Punycode of the given domain if it's non-ASCII."""
    return domain.encode("idna").decode("ascii")


def split_addr(addr, encoding="utf8"):
    """
    Split the address into local part and domain, properly encoded.
    When non-ascii characters are present in the local part, it must be
    MIME-word encoded. The domain name must be idna-encoded if it contains
    non-ascii characters.
    """
    print(addr)
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


def sanitize_address(addr, encoding="utf8"):
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

    # `email.headerregistry.Address` object is used since
    # email.utils.formataddr() naively encodes the name as ascii.
    if localpart and domain:
        address = Address(nm, username=localpart, domain=domain)
        return str(address)

    try:
        address = Address(nm, addr_spec=addr)
    except (InvalidHeaderDefect, NonASCIILocalPartDefect):
        localpart, domain = split_addr(addr, encoding)
        address = Address(nm, username=localpart, domain=domain)
    return str(address)


class CachedDNSName(object):
    """Cache the hostname, but do it lazily: socket.getfqdn() can take a
    couple of seconds, which slows down the restart of the server.
    """

    def get_fqdn(self):
        if not hasattr(self, "_fqdn"):
            self._fqdn = punycode(socket.getfqdn())
        return self._fqdn


DNS_NAME = CachedDNSName()
