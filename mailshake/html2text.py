# -*- coding: utf-8 -*-
import htmlentitydefs
import re


rx_body = re.compile(r'.*<body[^>]*>(.*)</body>', re.IGNORECASE | re.DOTALL)
rx_block = re.compile(
    (r'[\n\s]*<(address|article|aside|blockquote|fieldset'
     r'|Groups|h1|h2|h3|h4|h5|h6|header|hgroup|hr|p'
     r'|pre|section|table)[^>]*>[\n\s]*'),
    re.IGNORECASE
)
rx_tags = re.compile(r'</?[^>]+>', re.IGNORECASE | re.DOTALL)


def get_body(html):
    match = rx_body.match(html)
    if match:
        return match.group(1)
    return html


def replace_newlines(html):
    html = re.sub(rx_block, u'\n\n', html)
    html = re.sub(r'[\n\s]*<br>[\n\s]*', u'\n', html)
    return html


def unescape(html):
    def fixup(m):
        html = m.group(0)
        if html[:2] == "&#":
            try:
                if html[:3] == "&#x":
                    return unichr(int(html[3:-1], 16))
                else:
                    return unichr(int(html[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                html = unichr(htmlentitydefs.name2codepoint[html[1:-1]])
            except KeyError:
                pass
        return html # leave as is
    return re.sub(r"&#?\w+;", fixup, html)


def remove_tags(html):
    return re.sub(rx_tags, u'', html)


def remove_doubles(text):
    text = re.sub(r' +', u' ', text)
    text = re.sub(r'\n\n\n+', u'\n\n', text)
    return text.strip()


def extract_text_from_html(html):
    html = get_body(html)
    html = replace_newlines(html)
    html = unescape(html)
    text = remove_tags(html)
    text = remove_doubles(text)
    return text
