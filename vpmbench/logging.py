from logging import Formatter, Handler, DEBUG, StreamHandler, ERROR
from typing import List

from vpmbench import log


class LeveledFormatter(Formatter):
    _formats = {}

    def __init__(self, *args, **kwargs):
        super(LeveledFormatter, self).__init__(*args, **kwargs)

    def set_formatter(self, level, formatter):
        self._formats[level] = formatter

    def format(self, record):
        f = self._formats.get(record.levelno)
        if f is None:
            f = super(LeveledFormatter, self)
        return f.format(record)


def enable_logging(handlers: List[Handler] = [], log_level=DEBUG, enable_formatter=True):
    if len(handlers) == 0:
        handler = StreamHandler()
        if enable_formatter:
            formatter = LeveledFormatter('#### %(message)s')
            formatter.set_formatter(DEBUG, Formatter('- %(message)s'))
            formatter.set_formatter(ERROR, Formatter('- %(message)s'))
            handler.setFormatter(formatter)
        log.addHandler(handler)
    else:
        for handler in handlers:
            log.addHandler(handler)
    log.setLevel(log_level)
