# coding=utf-8
"""
    Mailer that writes messages to a file.
"""
import datetime
import errno
import os

from .. import _compat as compat
from .console import ToConsoleMailer


class ToFileMailer(ToConsoleMailer):

    def __init__(self, path, multifile=True, *args, **kwargs):
        assert isinstance(path, compat.string_types)
        path = os.path.abspath(path)
        if os.path.isfile(path):
            path = os.path.dirname(path)

        # Try to create it, if it not exists.
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise ValueError('Could not create directory for saving email'
                                 ' messages: %s (%s)' % (path, e))

        # Make sure that `path` exists and is writable.
        assert os.path.isdir(path)
        assert os.access(path, os.W_OK)

        self.path = path
        self.multifile = multifile
        self._fname = None

        # Finally, call super().
        # Since we're using the console-based backend as a base,
        # force the stream to be None, so we don't default to stdout
        kwargs['stream'] = None
        super(ToFileMailer, self).__init__(*args, **kwargs)

    def _get_filename(self):
        """Return a unique file name.
        """
        if self._fname is None:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d-%H%M%S")
            ms = now.microsecond
            fname = "%s-%s-%s.log" % (timestamp, abs(id(self)), ms)
            self._fname = os.path.join(self.path, fname)
        return self._fname

    def open(self):
        if self.stream is None:
            self.stream = open(self._get_filename(), 'a')
            return True
        return self.multifile

    def close(self):
        try:
            if self.stream is not None:
                self.stream.close()
        finally:
            self.stream = None
            if self.multifile:
                self._fname = None
