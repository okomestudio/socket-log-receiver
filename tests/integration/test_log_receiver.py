# -*- coding: utf-8 -*-
import logging
import logging.handlers
import random
import time
from contextlib import contextmanager
from typing import Generator

import pytest
from _pytest._py.path import LocalPath


@contextmanager
def waiter(receiver: LocalPath) -> Generator[None, None, None]:
    size_pre = receiver.size()
    yield
    t0 = time.time()
    while 1:
        size_post = receiver.size()
        if size_pre < size_post:
            break
        if time.time() - t0 > 3:
            raise Exception("Receiver does not appear to be receiving message(s)")


def random_message() -> str:
    return "Message to info " + str(random.random())


@pytest.mark.parametrize(
    "level", ["critical", "error", "warning", "info"]  # "debug" will hang
)
def test(receiver: LocalPath, level: str) -> None:
    rootLogger = logging.getLogger("")
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler(
        "localhost", logging.handlers.DEFAULT_TCP_LOGGING_PORT
    )
    rootLogger.addHandler(socketHandler)

    msg = random_message()

    with waiter(receiver):
        logger = getattr(logging, level)
        logger(msg)

    result = receiver.read()

    assert msg in result
