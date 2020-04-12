# -*- coding: utf-8 -*-
import logging

from .receivers import Receiver
from .receivers import configure_logging


def main():
    configure_logging()
    receiver = Receiver()
    logging.info("%r starting", receiver)
    receiver.serve()


if __name__ == "__main__":
    raise SystemExit(main())
