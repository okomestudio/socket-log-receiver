import logging
import logging.handlers
import signal

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
    "reloader": {
        "signal": "SIGHUP",
    },
}

config = ResConfig(default, load_on_init=False)


def handler(*args, **kwargs):
    config.load()


def reloader(reload_signal: str):
    """Configure config reloader."""
    try:
        sig = getattr(signal, reload_signal)
        assert isinstance(sig, signal.Signals)
    except (AttributeError, AssertionError):
        raise RuntimeError(f"Signal '{ reload_signal }' not recognized")
    signal.signal(sig, handler)
    logging.info("%s will reload config", sig)
