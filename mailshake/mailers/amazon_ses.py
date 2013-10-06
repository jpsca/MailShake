# -*- coding: utf-8 -*-
"""
    Mailer for Amazon Simple Email Server.
"""
from .base import BaseMailer


class AmazonSESMailer(BaseMailer):
    """A mailer for Amazon Simple Email Server.
    Requires the `boto` python library.
    """

    def __init__(self, region, aws_access_key_id, aws_secret_access_key,
                 return_path=None):
        """
        """
        import boto.ses

        self.conn = boto.ses.connect_to_region(
            region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        assert self.conn
        self.return_path = return_path
        super(AmazonSESMailer, self).__init__(*args, **kwargs)

    def send_messages(self, *email_messages):
        """
        """
        if not email_messages:
            return
        for msg in email_messages:
            data = {
                'source': msg.from_email,
                'subject': msg.subject,
                'to_addresses': msg.to,
                'cc_addresses': msg.cc,
                'bcc_addresses': msg.bcc,
                'reply_addresses': msg.reply_to,
                'reply_addresses': msg.reply_to,
                'format': 'html' if msg.html else 'text',
                'text_body': msg.text,
                'html_body': msg.html,
            }
            if self.return_path:
                data['return_path'] = self.return_path
            self.conn.send_email(**data)
