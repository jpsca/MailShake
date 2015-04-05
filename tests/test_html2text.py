# coding=utf-8
from mailshake.html2text import extract_text_from_html


def test_extract_text_from_full_html():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reset Password</title>
  <style>
  body {
    background: #f4f4f4;
    color: #444;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    margin: 0 auto;
    padding: 100px 0;
  }
  </style>
</head>
<body>
  <p>Dear username,</p>

  <p>In order to reset your password <br>
  just click the following link:</p>

  <p><a href="http://example.com/reset/qwertyuiop">http://example.com/reset/qwertyuiop</a></p>

  <hr>

  <p>Thank you.</p>
</body>
</html>"""

    expected = """Dear username,

In order to reset your password
just click the following link:

http://example.com/reset/qwertyuiop

Thank you."""

    text = extract_text_from_html(html)
    assert text == expected


def test_extract_text_from_html_fragment():
    html = """<p>Dear username,</p>

  <p>In order to reset your password <br>
  just click the following link:</p>

  <p><a href="http://example.com/reset/qwertyuiop">http://example.com/reset/qwertyuiop</a></p>

  <hr>

  <p>Thank you.</p>"""

    expected = """Dear username,

In order to reset your password
just click the following link:

http://example.com/reset/qwertyuiop

Thank you."""

    text = extract_text_from_html(html)
    assert text == expected
