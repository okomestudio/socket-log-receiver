# -*- coding: utf-8 -*-
import logging
from argparse import ArgumentParser

from .config import config
from .config import configure_logging
from .receivers import Receiver


def main():
    p = ArgumentParser()
    p.add_argument("--log-datefmt")
    p.add_argument("--log-filename")
    p.add_argument("--log-filemode")
    p.add_argument("--log-format")
    args = p.parse_args()

    config.prepare_from_argparse(args)
    config.load()

    configure_logging()
    receiver = Receiver()
    logging.info("%r starting", receiver)
    receiver.serve()


if __name__ == "__main__":
    raise SystemExit(main())
