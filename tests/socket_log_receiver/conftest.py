import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


def _record_as_attrdict(record):
    d = dict(record.__dict__)
    d["msg"] = record.getMessage()
    d["args"] = None
    d["exc_info"] = None
    d.pop("message", None)
    d.pop("__eq__", None)
    return d


@pytest.fixture(scope="module", autouse=True)
def patch_log_record():
    def __eq__(self, other):
        return _record_as_attrdict(self) == _record_as_attrdict(other)

    with patch("logging.LogRecord.__eq__", __eq__):
        yield


@pytest.fixture
def record():
    return logging.LogRecord("name", logging.DEBUG, "/path/to", 1, "message", (), None)


@pytest.fixture
def record_attrdict(record):
    return _record_as_attrdict(record)


@pytest.fixture
def server():
    return MagicMock(logname="foo")


@pytest.fixture
def response():
    return MagicMock()
