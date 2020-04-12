import logging
import os
import pickle
from logging.handlers import SocketHandler
from tempfile import NamedTemporaryFile

import pytest

from socket_log_receiver.receivers import Receiver
from socket_log_receiver.receivers import _Handler
from socket_log_receiver.receivers import configure_logging

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


class TestReceiver:
    def test_serve(self):
        receiver = Receiver(abort=1)
        with patch.object(receiver, "handle_request") as handle_request:
            with patch.object(receiver, "socket") as socket:
                socket.fileno.return_value = 1
                receiver.serve()
                handle_request.assert_called()

    def test_serve_timeout(self):
        receiver = Receiver(abort=1, timeout=0.01)
        with patch.object(receiver, "handle_request") as handle_request:
            receiver.serve()
            handle_request.assert_not_called()


class TestConfigureLogging:
    @pytest.fixture(autouse=True)
    def setup(self):
        handlers = logging.root.handlers
        logging.root.handlers.clear()
        yield
        logging.root.handlers = handlers

    def _get_only_stream_handler(self):
        handler = [
            h for h in logging.root.handlers if type(h) == logging.StreamHandler
        ][0]
        return handler

    @pytest.mark.parametrize("filemode", ["a", "a+", None])
    def test_filename(self, filemode):
        with NamedTemporaryFile() as f:
            os.environ["LOG_FILENAME"] = f.name
            if filemode is None:
                del os.environ["LOG_FILEMODE"]
            else:
                os.environ["LOG_FILEMODE"] = filemode
            with patch(
                "logging.handlers.WatchedFileHandler",
                wraps=logging.handlers.WatchedFileHandler,
            ) as init:
                configure_logging()
                init.assert_called_with(f.name, mode=filemode or "a+")
        handlers = logging.root.handlers
        assert any(isinstance(h, logging.handlers.WatchedFileHandler) for h in handlers)
        assert len([h for h in handlers if type(h) == logging.StreamHandler]) == 1

    def test_filename_missing(self):
        del os.environ["LOG_FILENAME"]
        configure_logging()
        handlers = logging.root.handlers
        assert all(
            not isinstance(h, logging.handlers.WatchedFileHandler) for h in handlers
        )
        assert len([h for h in handlers if type(h) == logging.StreamHandler]) == 1

    def test_format(self):
        format = "TEST:%(message)s"
        os.environ["LOG_FORMAT"] = format
        configure_logging()
        handler = self._get_only_stream_handler()
        assert format == handler.formatter._fmt

    def test_format_missing(self, record, record_attrdict):
        del os.environ["LOG_FORMAT"]
        configure_logging()
        handler = self._get_only_stream_handler()
        assert logging.BASIC_FORMAT == handler.formatter._fmt

    def test_datefmt(self):
        datefmt = "%Y"
        os.environ["LOG_DATEFMT"] = datefmt
        configure_logging()
        handler = self._get_only_stream_handler()
        assert datefmt == handler.formatter.datefmt

    def test_datefmt_missing(self):
        del os.environ["LOG_DATEFMT"]
        configure_logging()
        handler = self._get_only_stream_handler()
        assert None is handler.formatter.datefmt
