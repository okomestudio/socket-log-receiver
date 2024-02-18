import logging
import pickle
from logging.handlers import SocketHandler, WatchedFileHandler
from tempfile import NamedTemporaryFile
from typing import Any, Generator, Union
from unittest.mock import Mock, patch

import pytest

from socket_log_receiver.receivers import Receiver, _Handler, configure_logging


@pytest.fixture
def handler(response: Any, server: Receiver) -> _Handler:
    return _Handler(response, "localhost:9999", server)


class TestHandler:
    def test_handle(
        self, record: logging.LogRecord, response: Any, server: Receiver
    ) -> None:
        sh = SocketHandler("localhost", 9999)
        stream = sh.makePickle(record)

        idx = 0

        def recv(n: int) -> bytes:
            nonlocal idx
            s = stream[idx : idx + n]
            idx += n
            return s

        with patch.object(_Handler, "_handle_log_record") as handle_log_record:
            handler = _Handler(response, "localhost:9999", server)
            with patch.object(handler, "connection", new=Mock(recv=recv)):
                handler.handle()
            handle_log_record.assert_called_with(record)

    def test_unpickle(self, handler: _Handler, record_attrdict: dict) -> None:
        assert handler._unpickle(pickle.dumps(record_attrdict)) == record_attrdict

    @pytest.mark.parametrize("server_logname", ["foo", None])
    def test_handle_log_record_with_server_logname(
        self,
        handler: _Handler,
        record: logging.LogRecord,
        server: Receiver,
        server_logname: str,
    ) -> None:
        handler.server.logname = server_logname  # type: ignore
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


@pytest.mark.skip(reason="errors on OSError: [Errno 98] Address already in use")
class TestReceiver:
    def test_serve(self) -> None:
        receiver = Receiver("localhost", 982375, abort=1)
        with patch.object(receiver, "handle_request") as handle_request:
            with patch.object(receiver, "socket") as socket:
                socket.fileno.return_value = 1
                receiver.serve()
                handle_request.assert_called()

    def test_serve_timeout(self) -> None:
        receiver = Receiver("localhost", 928347, abort=1, timeout=0.01)
        with patch.object(receiver, "handle_request") as handle_request:
            receiver.serve()
            handle_request.assert_not_called()


class TestConfigureLogging:
    @pytest.fixture(autouse=True)
    def setup(self) -> Generator[None, None, None]:
        handlers = logging.root.handlers
        logging.root.handlers = []
        yield
        logging.root.handlers = handlers

    def _get_only_stream_handler(self) -> logging.StreamHandler:
        handler = [
            h for h in logging.root.handlers if type(h) == logging.StreamHandler
        ][0]
        return handler

    @pytest.fixture(autouse=True)
    def conf(self) -> Generator[dict, None, None]:
        yield {
            "filename": None,
            "filemode": "a+",
            "format": logging.BASIC_FORMAT,
            "datefmt": None,
            "level": "INFO",
        }

    @pytest.mark.parametrize("filemode", ["a", "a+", None])
    def test_filename(self, filemode: Union[str, None], conf: dict) -> None:
        configure_logging(1, {}, conf)

        with NamedTemporaryFile() as f:
            conf["filename"] = f.name
            if filemode is None:
                conf["filemode"] = "a+"
            else:
                conf["filemode"] = filemode
            with patch(
                "socket_log_receiver.receivers.WatchedFileHandler",
                wraps=WatchedFileHandler,
            ) as init:
                configure_logging(1, {}, conf)
                init.assert_called_with(f.name, mode=filemode or "a+")
        handlers = logging.root.handlers
        assert any(isinstance(h, WatchedFileHandler) for h in handlers)
        assert len([h for h in handlers if type(h) == logging.StreamHandler]) == 1

    def test_filename_missing(self, conf: dict) -> None:
        configure_logging(1, {}, conf)
        handlers = logging.root.handlers
        assert all(
            not isinstance(h, logging.handlers.WatchedFileHandler) for h in handlers
        )
        assert len([h for h in handlers if type(h) == logging.StreamHandler]) == 1

    def test_format(self, conf: dict) -> None:
        format = "TEST:%(message)s"
        conf["format"] = format

        configure_logging(1, {}, conf)

        handler = self._get_only_stream_handler()
        formatter = handler.formatter
        assert formatter is not None
        assert format == formatter._fmt

    def test_format_missing(
        self, record: logging.LogRecord, record_attrdict: dict, conf: dict
    ) -> None:
        configure_logging(1, {}, conf)

        handler = self._get_only_stream_handler()
        formatter = handler.formatter
        assert formatter is not None
        assert logging.BASIC_FORMAT == formatter._fmt

    def test_datefmt(self, conf: dict) -> None:
        datefmt = "%Y"
        conf["datefmt"] = datefmt

        configure_logging(1, {}, conf)

        handler = self._get_only_stream_handler()
        formatter = handler.formatter
        assert formatter is not None
        assert datefmt == formatter.datefmt

    def test_datefmt_missing(self, conf: dict) -> None:
        configure_logging(1, {}, conf)

        handler = self._get_only_stream_handler()
        formatter = handler.formatter
        assert formatter is not None
        assert None is formatter.datefmt
