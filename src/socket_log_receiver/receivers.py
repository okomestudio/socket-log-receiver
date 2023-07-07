# -*- coding: utf-8 -*-
import logging
import pickle
from select import select
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
            record = logging.makeLogRecord(obj)
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
        host,
        port,
        handler=_Handler,
        bind_and_activate=True,
        abort=0,
        timeout=1,
        logname=None,
    ):
        ThreadingTCPServer.__init__(
            self, (host, int(port)), handler, bind_and_activate=bind_and_activate
        )
        self.abort = abort
        self.timeout = timeout
        self.logname = logname

    def serve(self):
        abort = 0
        while not abort:
            rd, wr, ex = select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def serve(action, _, con):
    receiver = Receiver(con["host"], con["port"])
    logging.info("%r starting", receiver)
    receiver.serve()


def configure_logging(action, _, con):
    logging.root.setLevel(con["level"])

    handlers = []

    filename = con["filename"]
    if filename:
        mode = con["filemode"]
        handlers = [logging.handlers.WatchedFileHandler(filename, mode=mode)]

    if not any(type(h) == logging.StreamHandler for h in logging.root.handlers):
        handlers.append(logging.StreamHandler())

    format = con["format"]
    datefmt = con["datefmt"]
    formatter = logging.Formatter(format, datefmt)

    for handler in handlers:
        handler.setLevel(con["level"])
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
