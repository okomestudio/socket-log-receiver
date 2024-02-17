import logging
import logging.handlers
import signal
import platform

from resconfig import ResConfig

default = {
    "log": {
        "filename": None,
        "filemode": "a+",
        "format": logging.BASIC_FORMAT,
        "datefmt": None,
        "level": "INFO",
    },
    "receiver": {
        "host": "localhost",
        "port": logging.handlers.DEFAULT_TCP_LOGGING_PORT,
    },
}

config = ResConfig(default, load_on_init=False)


def handler(*args, **kwargs):
    config.load()

if platform.system() != 'Linux':
    signal.SIGHUP = 1

signal.signal(signal.SIGHUP, handler)
