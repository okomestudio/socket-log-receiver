# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from socket_log_receiver.config import config
from socket_log_receiver.config import reloader

from .receivers import configure_logging
from .receivers import serve


def main(argv=None):
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
    reloader(args.reload_signal)
    config.load()


if __name__ == "__main__":
    raise SystemExit(main())
