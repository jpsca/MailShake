# -*- coding: utf-8 -*-
"""
    # mailshake.utils

    Email sending related helper functions.

"""
from email.header import Header
from email.utils import formataddr, parseaddr
import os
import random
import socket
import time

from shake import to_unicode


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


def sanitize_address(addr, encoding):
    if isinstance(addr, basestring):
        addr = parseaddr(to_unicode(addr))
    nm, addr = addr
    nm = str(Header(nm, encoding))
    try:
        addr = addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if u'@' in addr:
            localpart, domain = addr.split(u'@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna')
            addr = '@'.join([localpart, domain])
        else:
            addr = str(Header(addr, encoding))
    return formataddr((nm, addr))



# Copied from Python standard library, with the following modifications:
# * Used cached hostname for performance.
# * Added try/except to support lack of getpid() in Jython (#5496).
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
        # No getpid() in Jython, for example.
        pid = 1
    randint = random.randrange(100000)
    if idstring is None:
        idstring = ''
    else:
        idstring = '.' + idstring
    idhost = DNS_NAME
    msgid = '<%s.%s.%s%s@%s>' % (utcdate, pid, randint, idstring, idhost)
    return msgid

