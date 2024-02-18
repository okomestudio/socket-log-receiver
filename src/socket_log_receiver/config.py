import logging
import logging.handlers
import signal
from types import FrameType
from typing import Optional

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


def reloader(signal_number: int, stack_frame: Optional[FrameType]) -> None:
    config.load()


def setup_reloader(reload_signal: str) -> None:
    """Configure config reloader."""
    try:
        sig = getattr(signal, reload_signal)
        assert isinstance(sig, signal.Signals)
    except (AttributeError, AssertionError):
        raise RuntimeError(f"Signal '{ reload_signal }' not recognized")
    signal.signal(sig, reloader)
    logging.info("%s will reload config", sig)
