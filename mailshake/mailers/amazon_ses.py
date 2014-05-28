# -*- coding: utf-8 -*-
"""
    Mailer for Amazon Simple Email Server.
"""
import logging

from .base import BaseMailer


class AmazonSESMailer(BaseMailer):
    """A mailer for Amazon Simple Email Server.
    Requires the `boto` python library.
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 return_path=None, *args, **kwargs):
        """
        """
        from boto.ses.connection import SESConnection

        self.conn = SESConnection(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        assert self.conn
        self.return_path = return_path
        super(AmazonSESMailer, self).__init__(*args, **kwargs)

    def send_messages(self, *email_messages):
        """
        """
        logger = logging.getLogger('mailshake:AmazonSESMailer')
        if not email_messages:
            logger.debug('No email messages to send')
            return

        for msg in email_messages:
            data = {
                'source': msg.from_email,
                'subject': msg.subject,
                'body': msg.html or msg.text,
                'to_addresses': msg.to,

                'cc_addresses': msg.cc or None,
                'bcc_addresses': msg.bcc or None,
                'reply_addresses': msg.reply_to or None,
                'format': 'html' if msg.html else 'text',
            }
            if self.return_path:
                data['return_path'] = self.return_path
            logger.debug('Sending email from {0} to {1}'.format(msg.from_email, msg.to))
            self.conn.send_email(**data)
