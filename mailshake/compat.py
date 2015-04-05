# coding=utf-8
import sys


PY2 = sys.version_info[0] == 2

if PY2:
    from htmlentitydefs import name2codepoint
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
    import codecs

    text_type = unicode
    binary_type = str
    string_types = (binary_type, text_type)

    def to_unicode(s):
        return codecs.unicode_escape_decode(s)[0]

    def to_native(s, encoding='utf-8'):
        if isinstance(s, text_type):
            return s.encode(encoding)
        elif s and encoding != 'utf-8':
            return s.decode('utf-8').encode(encoding)
        return s

else:
    from io import StringIO
    from html.entities import name2codepoint

    text_type = str
    binary_type = bytes
    string_types = (text_type, )

    def to_unicode(s):
        return s

    def to_native(s, encoding='utf-8'):
        return s
