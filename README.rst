
.. image:: https://raw.github.com/jpscaletti/mailshake/master/docs/static/images/mailshake@2x.png
   :alt: Mailshake logo

===========================
Mailshake
===========================

.. image:: https://travis-ci.org/jpscaletti/MailShake.svg?branch=master
   :target: https://travis-ci.org/jpscaletti/MailShake
   :alt: Build Status

Although Python makes sending email relatively easy via the smtplib module,
this library provides a couple of light wrappers over it.

These wrappers make sending email extra quick, easy to test email sending during
development, and provides support for platforms that can’t use SMTP.

*Compatible with Python 3.4+, 2.6+ and pypy.*

Mailers availiable:

* SMTPMailer
* AmazonSESMailer
* ToConsoleMailer (prints the emails in the console)
* ToFileMailer (save the emails in a file)
* ToMemoryMailer (for testing)
* DummyMailer (does nothing)

Usage:

.. code:: python

    from mailshake import SMTPMailer

    mailer = SMTPMailer()
    mailer.send(
        subject='Hi',
        text_content='Hello world!',
        from_email='from@example.com',
        to=['mary@example.com', 'bob@example.com']
    )

You can also compose several messages and send them at the same time:

.. code:: python

    from mailshake import SMTPMailer, EmailMessage

    mailer = SMTPMailer()
    messages = []

    email_msg = EmailMessage(
        "Weekend getaway",
        "Here's a photo of us from our trip.",
        "from@example.com",
        "bob@example.com"
    )
    email_msg.attach_file("picture.jpg")
    messages.append(email_msg)

    #…

    mailer.send_messages(*messages)


Contributing
======================

#. Check for `open issues <https://github.com/jpscaletti/Mailshake/issues>`_ or open
   a fresh issue to start a discussion around a feature idea or a bug.
#. Fork the `Mailshake repository on Github <https://github.com/jpscaletti/Mailshake>`_
   to start making your changes.
#. Write a test which shows that the bug was fixed or that the feature works
   as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.
   :) Make sure to add yourself to ``AUTHORS``.


Run the tests
======================

We use some external dependencies, listed in ``requirements_tests.txt``::

    $  pip install -r requirements-tests.txt
    $  python setup.py install

To run the tests in your current Python version do::

    $  make test

To run them in every supported Python version do::

    $  tox

It's also neccesary to run the coverage report to make sure all lines of code
are touch by the tests::

    $  make coverage

Our test suite `runs continuously on Travis CI <https://travis-ci.org/jpscaletti/Mailshake>`_ with every update.

______

:copyright: `Juan-Pablo Scaletti <http://jpscaletti.com/>`_.
:logo: by `Alfonso Mello <http://www.alfonsomello.com/>`_.
:license: MIT, see LICENSE for more details.
