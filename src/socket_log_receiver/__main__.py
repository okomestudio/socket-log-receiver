# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from .config import config
from .receivers import configure_logging
from .receivers import serve


def main():
    p = ArgumentParser()
    p.add_argument("--conf")
    config.add_arguments_to_argparse(p)
    args = p.parse_args()
    config.prepare_from_argparse(args, config_file_arg="conf")
    config.register("log", configure_logging)
    config.register("receiver", serve)
    config.load()


if __name__ == "__main__":
    raise SystemExit(main())
