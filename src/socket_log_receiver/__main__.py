# -*- coding: utf-8 -*-
import logging
from argparse import ArgumentParser

from .config import config
from .config import configure_logging
from .receivers import Receiver


def main():
    p = ArgumentParser()
    config.add_arguments_to_argparse(p)
    args = p.parse_args()

    config.prepare_from_argparse(args)
    config.load()

    configure_logging()
    receiver = Receiver()
    logging.info("%r starting", receiver)
    receiver.serve()


if __name__ == "__main__":
    raise SystemExit(main())
