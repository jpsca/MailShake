# coding=utf-8
"""
    Mailer that writes messages to console instead of sending them. Ideal
    for development.
"""
import sys
import threading

from .. import _compat as compat
from .base import BaseMailer


class ToConsoleMailer(BaseMailer):

    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(ToConsoleMailer, self).__init__(*args, **kwargs)

    def write_message(self, message):
        msg = message.render()
        msg_data = msg.as_bytes()
        if compat.PY3:
            _charset = msg.get_charset()
            if _charset and _charset.get_output_charset:
                _charset = _charset.get_output_charset()
            charset = _charset or 'utf-8'
            msg_data = msg_data.decode(charset)
        self.stream.write('%s\n' % msg_data)
        self.stream.write('-' * 79)
        self.stream.write('\n')

    def send_messages(self, *email_messages):
        """Write all messages to the stream in a thread-safe way."""
        if not email_messages:
            return
        msg_count = 0
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self.write_message(message)
                    self.stream.flush()  # flush after each message
                    msg_count += 1
                if stream_created:
                    self.close()
            except Exception:
                if not self.fail_silently:
                    raise
        return msg_count
