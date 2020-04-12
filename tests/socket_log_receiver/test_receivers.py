import logging
import pickle
from logging.handlers import SocketHandler

import pytest

from socket_log_receiver.receivers import _Handler

try:
    from unittest.mock import MagicMock, Mock, patch
except ImportError:
    from mock import MagicMock, Mock, patch


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


@pytest.fixture
def handler(response, server):
    return _Handler(response, "localhost:9999", server)


class TestHandler:
    def test_handle(self, record, response, server):
        sh = SocketHandler("localhost", "9999")
        stream = sh.makePickle(record)

        idx = 0

        def recv(n):
            nonlocal idx
            s = stream[idx : idx + n]
            idx += n
            return s

        with patch.object(_Handler, "_handle_log_record") as handle_log_record:
            handler = _Handler(response, "localhost:9999", server)
            with patch.object(handler, "connection", new=Mock(recv=recv)) as conn:
                handler.handle()
            handle_log_record.assert_called_with(record)

    def test_unpickle(self, handler, record_attrdict):
        assert handler._unpickle(pickle.dumps(record_attrdict)) == record_attrdict

    @pytest.mark.parametrize("server_logname", ["foo", None])
    def test_handle_log_record_with_server_logname(
        self, handler, record, server, server_logname
    ):
        handler.server.logname = server_logname
        logger = Mock()
        with patch(
            "socket_log_receiver.receivers.logging.getLogger",
            new=Mock(return_value=logger),
        ) as getLogger:
            handler._handle_log_record(record)
        getLogger.assert_called_once_with(
            server.logname if server_logname else record.name
        )
        logger.handle.assert_called_once_with(record)
