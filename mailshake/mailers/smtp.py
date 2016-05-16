# coding=utf-8
"""
    SMTP mailer.
"""
try:
    import smtplib
    import ssl
    import threading
except ImportError:
    threading = None

from .base import BaseMailer
from ..utils import sanitize_address, DNS_NAME


class SMTPMailer(BaseMailer):

    """A wrapper that manages the SMTP network connection.
    """

    def __init__(self, host='localhost', port=587, username=None, password=None,
                 use_tls=None, use_ssl=None, timeout=None, *args, **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = bool(use_tls)
        self.use_ssl = bool(use_ssl)
        self.timeout = timeout
        if self.use_ssl and self.use_tls:
            raise ValueError("EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive")

        self.connection = None
        # Some limited environments, like GAE, does not have a functional threading module
        self._lock = threading.RLock() if threading else None
        super(SMTPMailer, self).__init__(*args, **kwargs)

    def open(self, hostname=None):
        """Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection_params = {'local_hostname': DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout

        try:
            self.connection = smtplib.SMTP(self.host, self.port, **connection_params)

            if self.use_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
                self.connection.ehlo()
                self.connection.starttls(context)
                self.connection.ehlo()
            elif self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()
                self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)

        except:
            if not self.fail_silently:
                raise

        return True

    def close(self):
        """Closes the connection to the email server.
        """
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                self.connection.close()
            except:
                if not self.fail_silently:
                    raise
        finally:
            self.connection = None

    def send_messages(self, *email_messages):
        """Sends one or more EmailMessage objects and returns the number of
        messages sent.
        """
        if not email_messages:
            return
        with self._lock:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open(), trying to send would be pointless.
                return
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending.
        """
        recipients = email_message.get_recipients()
        if not recipients:
            return False
        from_email = email_message.from_email or self.default_from
        from_email = sanitize_address(from_email, email_message.encoding)
        recipients = [
            sanitize_address(addr, email_message.encoding)
            for addr in recipients
        ]
        try:
            self.connection.sendmail(
                from_email, recipients, email_message.as_bytes()
            )
        except:
            if not self.fail_silently:
                raise
            return False
        return True
