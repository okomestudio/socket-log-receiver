# -*- coding: utf-8 -*-
import logging
import os
import pickle
from logging.handlers import WatchedFileHandler
from select import select
from socketserver import StreamRequestHandler, ThreadingTCPServer
from struct import unpack
from typing import Any, List, Optional, Type, Union


class _Handler(StreamRequestHandler):
    """Handler for log record pickled by logging.handlers.SocketHandler.

    The SocketHandler.makePickle(record) streams the data according to

    >>> data = pickle.dumps(record_attr_dict, 1)
    >>> datalen = struct.pack('>L', len(data))
    >>> datalen + data  # this will be streamed to socket

    Basically the first four bytes contains the data length of the
    pickled log record.
    """

    def handle(self) -> None:
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = unpack(">L", chunk)[0]  # big-endian (>), unsigned long (L)
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self._unpickle(chunk)
            record = logging.makeLogRecord(obj)
            self._handle_log_record(record)

    def _unpickle(self, data: bytes) -> Any:
        return pickle.loads(data)

    def _handle_log_record(self, record: logging.LogRecord) -> None:
        if hasattr(self.server, "logname") and self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        logger.handle(record)


class Receiver(ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(
        self,
        host: str,
        port: Union[int, str],
        handler: Type[StreamRequestHandler] = _Handler,
        bind_and_activate: bool = True,
        abort: int = 0,
        timeout: float = 1.0,
        logname: Optional[str] = None,
    ):
        ThreadingTCPServer.__init__(
            self, (host, int(port)), handler, bind_and_activate=bind_and_activate
        )
        self.abort = abort
        self.timeout = timeout
        self.logname = logname

    def serve(self) -> None:
        abort = 0
        while not abort:
            rd, wr, ex = select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def serve(action: int, _: dict, con: dict) -> None:
    receiver = Receiver(con["host"], con["port"])
    logging.info("%r starting (PID: %d)", receiver, os.getpid())
    receiver.serve()


def configure_logging(action: int, _: dict, con: dict) -> None:
    logging.root.setLevel(con["level"])

    handlers: List[logging.Handler] = []

    filename = con["filename"]
    if filename:
        mode = con["filemode"]
        handlers = [WatchedFileHandler(filename, mode=mode)]

    if not any(type(h) == logging.StreamHandler for h in logging.root.handlers):
        handlers.append(logging.StreamHandler())

    format = con["format"]
    datefmt = con["datefmt"]
    formatter = logging.Formatter(format, datefmt)

    for handler in handlers:
        handler.setLevel(con["level"])
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
