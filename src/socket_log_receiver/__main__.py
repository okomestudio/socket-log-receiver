# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from typing import List, Optional

from socket_log_receiver.config import config, setup_reloader

from .receivers import configure_logging, serve


def main(argv: Optional[List[str]] = None) -> None:
    p = ArgumentParser()
    p.add_argument("--conf")
    config.add_arguments_to_argparse(p)
    args = p.parse_args(argv)
    config.prepare_from_argparse(args, config_file_arg="conf")
    config.register("log", configure_logging)
    config.register("receiver", serve)
    config.register("reloader", setup_reloader)
    config.load()


if __name__ == "__main__":
    raise SystemExit(main())  # type: ignore
