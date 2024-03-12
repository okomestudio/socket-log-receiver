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


_original_handler = None


def setup_reloader(action: int, _: dict, con: dict) -> None:
    reloader_signal = con["signal"]
    try:
        sig = getattr(signal, reloader_signal)
        assert isinstance(sig, signal.Signals)
    except (AttributeError, AssertionError):
        raise RuntimeError(f"Signal '{ reloader_signal }' not recognized")

    # Restore signal handler if previously replaced
    global _original_handler
    if _original_handler:
        signal.signal(*_original_handler)

    replaced_handler = signal.signal(sig, reloader)
    _original_handler = (sig, replaced_handler)

    logging.info("%s will reload config", sig)
