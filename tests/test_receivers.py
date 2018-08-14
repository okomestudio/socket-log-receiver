# -*- coding: utf-8 -*-
import logging
import logging.handlers
import random
import time
from contextlib import contextmanager

import pytest


@contextmanager
def waiter(receiver):
    size_pre = receiver.size()
    yield
    t0 = time.time()
    while 1:
        size_post = receiver.size()
        if size_pre < size_post:
            break
        if time.time() - t0 > 3:
            raise Exception(
                'Receiver does not appear to be receiving message(s)')


def random_message():
    return 'Message to info ' + str(random.random())


@pytest.mark.parametrize('level', [
    'critical',
    'error',
    'warning',
    'info',
    'debug',
])
def test(receiver, level):
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler(
        'localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    rootLogger.addHandler(socketHandler)

    msg = random_message()

    with waiter(receiver):
        logger = getattr(logging, level)
        logger(msg)

    result = receiver.read()

    assert msg in result
