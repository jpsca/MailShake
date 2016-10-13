# coding=utf-8
from email.header import Header
from email.utils import formataddr, parseaddr, getaddresses
import os
import random
import socket
import time

from . import _compat as compat


class CachedDnsName(object):
    """Cache the hostname, but do it lazily: socket.getfqdn() can take a
    couple of seconds, which slows down the restart of the server.
    """

    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, '_fqdn'):
            self._fqdn = socket.getfqdn()
        return self._fqdn


DNS_NAME = CachedDnsName()


def sanitize_address(addr, encoding='utf8'):
    if isinstance(addr, compat.string_types):
        addr = parseaddr(compat.force_text(addr))
    nm, addr = addr
    nm = str(Header(nm, encoding))
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if u'@' in addr:
            localpart, domain = addr.split(u'@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna')
            addr = '@'.join([localpart, domain])
        else:
            addr = str(Header(addr, encoding))
    return formataddr((nm, addr))


def make_msgid(idstring=None):
    """Returns a string suitable for RFC 2822 compliant Message-ID, e.g:

    <20020201195627.33539.96671@nightshade.la.mastaler.com>

    Optional idstring if given is a string used to strengthen the
    uniqueness of the message id.
    """
    timeval = time.time()
    utcdate = time.strftime('%Y%m%d%H%M%S', time.gmtime(timeval))
    try:
        pid = os.getpid()
    except AttributeError:
        pid = 1
    randint = random.randrange(100000)
    if idstring is None:
        idstring = ''
    else:
        idstring = '.' + idstring
    idhost = DNS_NAME
    msgid = '<%s.%s.%s%s@%s>' % (utcdate, pid, randint, idstring, idhost)
    return msgid


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


def forbid_multi_line_headers(name, val, encoding='utf-8'):
    """Forbids multi-line headers, to prevent header injection.
    """
    val = compat.force_text(val)
    if '\n' in val or '\r' in val:
        raise ValueError(
            "Header values can't contain newlines "
            "(got {val} for header {name})".format(val=val, name=name)
        )
    try:
        val.encode('ascii')
    except UnicodeEncodeError:
        if name.lower() in ADDRESS_HEADERS:
            val = ', '.join([
                sanitize_address(addr, encoding)
                for addr in getaddresses((val,))
            ])
        else:
            val = Header(val, encoding).encode()
    else:
        if name.lower() == 'subject':
            val = Header(val).encode()
    return str(name), val
