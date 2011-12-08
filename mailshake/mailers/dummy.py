# -*- coding: utf-8 -*-
"""
    # mailshake.mailers.dummy

    Dummy mailer that does nothing.

"""
from .base import BaseMailer


class DummyMailer(BaseMailer):

    def send(self, *email_messages):
        return len(email_messages)

