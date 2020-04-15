import logging
import os
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest
from socket_log_receiver.config import config
from socket_log_receiver.config import configure_logging


class TestConfigureLogging:
    @pytest.fixture(autouse=True)
    def setup(self):
        handlers = logging.root.handlers
        logging.root.handlers = []
        yield
        logging.root.handlers = handlers

    def _get_only_stream_handler(self):
        handler = [
            h for h in logging.root.handlers if type(h) == logging.StreamHandler
        ][0]
        return handler

    def _call_configure_logging(self):
        config.load()
        configure_logging()

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
                self._call_configure_logging()
                init.assert_called_with(f.name, mode=filemode or "a+")
        handlers = logging.root.handlers
        assert any(isinstance(h, logging.handlers.WatchedFileHandler) for h in handlers)
        assert len([h for h in handlers if type(h) == logging.StreamHandler]) == 1

    def test_filename_missing(self):
        del os.environ["LOG_FILENAME"]
        self._call_configure_logging()
        handlers = logging.root.handlers
        assert all(
            not isinstance(h, logging.handlers.WatchedFileHandler) for h in handlers
        )
        assert len([h for h in handlers if type(h) == logging.StreamHandler]) == 1

    def test_format(self):
        format = "TEST:%(message)s"
        os.environ["LOG_FORMAT"] = format
        self._call_configure_logging()
        handler = self._get_only_stream_handler()
        assert format == handler.formatter._fmt

    def test_format_missing(self, record, record_attrdict):
        del os.environ["LOG_FORMAT"]
        self._call_configure_logging()
        handler = self._get_only_stream_handler()
        assert logging.BASIC_FORMAT == handler.formatter._fmt

    def test_datefmt(self):
        datefmt = "%Y"
        os.environ["LOG_DATEFMT"] = datefmt
        self._call_configure_logging()
        handler = self._get_only_stream_handler()
        assert datefmt == handler.formatter.datefmt

    def test_datefmt_missing(self):
        del os.environ["LOG_DATEFMT"]
        self._call_configure_logging()
        handler = self._get_only_stream_handler()
        assert None is handler.formatter.datefmt
