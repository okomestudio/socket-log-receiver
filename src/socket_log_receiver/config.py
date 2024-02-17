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
    "reloader": {
        "signal": "SIGHUP",
    },
}

config = ResConfig(default, load_on_init=False)


def handler(*args, **kwargs):
    config.load()

if platform.system() != 'Linux':
    signal.SIGHUP = 1

def reloader(reload_signal):
    # reloader_signal = config.get("reloader.signal", "SIGHUP")
    print("FF", reload_signal)
    logging.info("HERE")
    try:
        sig = getattr(signal, reload_signal)
    except AttributeError:
        raise RuntimeError(f"Signal '{ reload_signal }' not recognized")
    logging.info("%s will reload config", sig)
    signal.signal(sig, handler)
    logging.info("%s will reload config", sig)
