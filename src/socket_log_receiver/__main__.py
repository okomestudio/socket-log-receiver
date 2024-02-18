# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from typing import List, Optional

from socket_log_receiver.config import config, setup_reloader

from .receivers import configure_logging, serve


def main(argv: Optional[List[str]] = None) -> None:
    p = ArgumentParser()
    p.add_argument("--conf")
    p.add_argument(
        "--reload-signal",
        default="SIGHUP",
        help="Signal to reload config.",
    )
    config.add_arguments_to_argparse(p)
    args = p.parse_args(argv)
    config.prepare_from_argparse(args, config_file_arg="conf")
    config.register("log", configure_logging)
    config.register("receiver", serve)
    setup_reloader(args.reload_signal)
    config.load()


if __name__ == "__main__":
    raise SystemExit(main())  # type: ignore
