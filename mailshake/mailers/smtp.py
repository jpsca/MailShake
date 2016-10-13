# coding=utf-8
"""
    SMTP mailer.
"""
import smtplib
import ssl


from .base import BaseMailer
from ..utils import DNS_NAME


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class SMTPMailer(BaseMailer):

    """A wrapper that manages the SMTP network connection.

    `max_recipients`: Number of maximum recipients per mesage
        Mailshake send several messages instead of one, in order to stay inside
        that limit.

    """

    def __init__(self, host='localhost', port=587, username=None, password=None,
                 use_tls=None, use_ssl=None, timeout=None, max_recipients=200,
                 *args, **kwargs):
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
        self.max_recipients = max_recipients
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

    def _send(self, message):
        """A helper method that does the actual sending.
        """
        recipients = message.get_recipients()
        if not recipients:
            return False
        from_email = message.from_email or self.default_from
        to_set = set(message.to)
        cc_set = set(message.cc)
        bcc_set = set(message.bcc)
        try:
            # Your SMTP provider has limits!
            for group in chunker(recipients, self.max_recipients):
                group_set = set(group)
                message.to = list(to_set.intersection(group_set))
                message.cc = list(cc_set.intersection(group_set))
                message.bcc = list(bcc_set.intersection(group_set))
                self.connection.sendmail(
                    from_email, group, message.as_bytes()
                )
        except:
            if not self.fail_silently:
                raise
            return False
        return True
