# -*- coding: utf-8 -*-
"""
    # mailshake.mailers.base

    Base mailer class.

"""

class BaseMailer(object):
    """Base class for mailers implementations.

    Subclasses must at least overwrite send().
    """

    def __init__(self, default_from=None, fail_silently=False, *args, **kwargs):
        self.default_from = default_from
        self.fail_silently = fail_silently
    
    def open(self):
        """Open a network connection.

        This method can be overwritten by mailer implementations to
        open a network connection.

        It's up to the implementation to track the status of
        a network connection if it's needed by the mailer.

        This method can be called by applications to force a single
        network connection to be used when sending mails. See the
        `send()` method of the `SMTPMailer` for a reference
        implementation.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection.

        Like `open()`, the default implementation does nothing.
        """
        pass

    def send(self, **email_messages):
        """Sends one or more `EmailMessage` objects and returns the number of
        email messages sent.
        """
        raise NotImplementedError

