# coding=utf-8
"""
    Mailer for Amazon Simple Email Server.
"""
import logging

from .base import BaseMailer


class AmazonSESMailer(BaseMailer):
    """A mailer for Amazon Simple Email Server.
    Requires the `boto3` python library.
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 region_name='us-east-1', return_path=None, *args, **kwargs):
        """
        """
        import boto3

        self.client = boto3.client(
            'ses',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        assert self.client
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
            destination_data = {
                'ToAddresses': msg.to,
            }
            if msg.cc:
                destination_data['CcAddresses'] = msg.cc
            if msg.bcc:
                destination_data['BccAddresses'] = msg.bcc

            body_data = {
                'Text': {
                    'Data': msg.text,
                    'Charset': 'utf8'
                }
            }
            if msg.html:
                body_data['Html'] = {
                    'Data': msg.html,
                    'Charset': 'utf8',
                }

            data = {
                'Source': msg.from_email,
                'Destination': destination_data,
                'Message': {
                    'Subject': {
                        'Data': msg.subject,
                        'Charset': 'utf8',
                    },
                    'Body': body_data,
                },
            }
            if msg.reply_to:
                data['ReplyAddresses'] = msg.reply_to
            if self.return_path:
                data['ReturnPath'] = self.return_path

            logger.debug('Sending email from {0} to {1}'.format(msg.from_email, msg.to))
            self.client.send_email(**data)
