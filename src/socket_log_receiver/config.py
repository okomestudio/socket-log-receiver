import logging

from resconfig import ResConfig

default = {
    "log": {
        "filename": None,
        "filemode": "a+",
        "format": logging.BASIC_FORMAT,
        "datefmt": None,
        "level": "INFO",
    }
}

config = ResConfig(default, load_on_init=False)


def configure_logging():
    logging.root.setLevel(config["log.level"])

    handlers = []

    filename = config["log.filename"]
    if filename:
        mode = config["log.filemode"]
        handlers = [logging.handlers.WatchedFileHandler(filename, mode=mode)]

    if not any(type(h) == logging.StreamHandler for h in logging.root.handlers):
        handlers.append(logging.StreamHandler())

    format = config["log.format"]
    datefmt = config["log.datefmt"]
    formatter = logging.Formatter(format, datefmt)

    for handler in handlers:
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
