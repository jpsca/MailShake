# -*- coding: utf-8 -*-
import sys


PY2 = sys.version_info[0] == 2
string_types = (str, unicode) if PY2 else (str,)


def to_unicode(s, encoding='utf-8', errors='strict'):
    """Returns a unicode object representing 's'. Treats bytestrings using the
    `encoding` codec.
    """
    if isinstance(s, unicode):
        return s
    try:
        return unicode(s, encoding, errors)
    except UnicodeDecodeError as e:
        if isinstance(s, Exception):
            return u' '.join([to_unicode(arg, encoding, strings_only,
                errors) for arg in s])
        raise UnicodeDecodeError(s, *e.args)            


def to_bytestring(s, encoding='utf-8', errors='strict'):
    """Returns a bytestring version of 's', encoded as specified in 'encoding'.
    """
    if isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    return s
