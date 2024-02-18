import logging
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


def _record_as_attrdict(record: logging.LogRecord) -> dict:
    d = dict(record.__dict__)
    d["msg"] = record.getMessage()
    d["args"] = None
    d["exc_info"] = None
    d.pop("message", None)
    d.pop("__eq__", None)
    return d


@pytest.fixture(scope="module", autouse=True)
def patch_log_record() -> Generator[None, None, None]:
    def __eq__(self: logging.LogRecord, other: logging.LogRecord) -> bool:
        return _record_as_attrdict(self) == _record_as_attrdict(other)

    with patch("logging.LogRecord.__eq__", __eq__):
        yield


@pytest.fixture
def record() -> logging.LogRecord:
    return logging.LogRecord("name", logging.DEBUG, "/path/to", 1, "message", (), None)


@pytest.fixture
def record_attrdict(record: logging.LogRecord) -> dict:
    return _record_as_attrdict(record)


@pytest.fixture
def server() -> MagicMock:
    return MagicMock(logname="foo")


@pytest.fixture
def response() -> MagicMock:
    return MagicMock()
