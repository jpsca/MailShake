# coding=utf-8
import sys


PY_VERSION = sys.version_info
PY2 = PY_VERSION[0] == 2
PY3 = not PY2

if PY2:
    from htmlentitydefs import name2codepoint  # noqa
    try:
        from cStringIO import StringIO  # noqa
    except ImportError:
        from StringIO import StringIO  # noqa
    from io import BytesIO  # noqa

    text_type = unicode
    binary_type = str
    string_types = (binary_type, text_type)
    unichr = unichr

else:
    from io import StringIO, BytesIO  # noqa
    from html.entities import name2codepoint  # noqa

    text_type = str
    binary_type = bytes
    string_types = (text_type, )
    unichr = chr


def force_text(s, encoding='utf-8', errors='strict'):
    """Force a string to be the native text_type
    """
    if isinstance(s, text_type):
        return s

    if not isinstance(s, string_types):
        if PY3:
            if isinstance(s, bytes):
                s = text_type(s, encoding, errors)
            else:
                s = text_type(s)
        elif hasattr(s, '__unicode__'):
            s = text_type(s)
        else:
            s = text_type(bytes(s), encoding, errors)
    else:
        s = s.decode(encoding, errors)

    return s
