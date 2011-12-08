# -*- coding: utf-8 -*-
"""
    # mailshake.mailers.memory

    Mailer for testing.

"""
from .base import BaseMailer


class ToMemoryMailer(BaseMailer):
    """A mailer for use during test sessions.

    The test connection stores email messages in a dummy outbox,
    rather than sending them out on the wire.

    The dummy outbox is accessible through the outbox instance attribute.
    """
    def __init__(self, *args, **kwargs):
        self.outbox = []
        super(ToMemoryMailer, self).__init__(*args, **kwargs)
    
    def send(self, *email_messages):
        """Redirect messages to the dummy outbox"""
        self.outbox.extend(email_messages)
        return len(email_messages)

