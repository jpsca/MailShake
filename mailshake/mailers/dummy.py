# coding=utf-8
"""
    Dummy mailer that does nothing.
"""
from .base import BaseMailer


class DummyMailer(BaseMailer):

    def send_messages(self, *email_messages):
        return len(email_messages)
