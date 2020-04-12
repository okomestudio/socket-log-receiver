# -*- coding: utf-8 -*-
import logging
import logging.handlers
import os
import pickle
from struct import unpack

try:
    from socketserver import StreamRequestHandler
    from socketserver import ThreadingTCPServer
except ImportError:
    # For Python 2.7
    from SocketServer import StreamRequestHandler
    from SocketServer import ThreadingTCPServer


class _Handler(StreamRequestHandler):
    """Handler for log record pickled by logging.handlers.SocketHandler.

    The SocketHandler.makePickle(record) streams the data according to

    >>> data = pickle.dumps(record_attr_dict, 1)
    >>> datalen = struct.pack('>L', len(data))
    >>> datalen + data  # this will be streamed to socket

    Basically the first four bytes contains the data length of the pickled log record.
    """

    def handle(self):
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = unpack(">L", chunk)[0]  # big-endian (>), unsigned long (L)
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self._unpickle(chunk)
            print(obj)
            record = logging.makeLogRecord(obj)
            print(record)
            self._handle_log_record(record)

    def _unpickle(self, data):
        return pickle.loads(data)

    def _handle_log_record(self, record):
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        logger.handle(record)


class Receiver(ThreadingTCPServer):

    allow_reuse_address = True

    def __init__(
        self,
        host="0.0.0.0",
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        handler=_Handler,
    ):
        ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve(self):
        import select

        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def configure_logging():
    filename = os.environ.get("LOG_FILENAME") or None
    if filename:
        mode = os.environ.get("LOG_FILEMODE") or "a"
        handlers = [
            logging.handlers.WatchedFileHandler(filename, mode=mode),
            logging.StreamHandler(),
        ]
    else:
        handlers = [logging.StreamHandler()]

    format = os.environ.get("LOG_FORMAT") or logging.BASIC_FORMAT
    datefmt = os.environ.get("LOG_DATEFMT") or None
    formatter = logging.Formatter(format, datefmt)

    for handler in handlers:
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    logging.root.setLevel("INFO")
