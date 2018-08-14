# -*- coding: utf-8 -*-
import logging
import logging.handlers
import pickle
import struct
try:
    from socketserver import StreamRequestHandler
    from socketserver import ThreadingTCPServer
except ImportError:
    # For Python 2.7
    from SocketServer import StreamRequestHandler
    from SocketServer import ThreadingTCPServer


class Handler(StreamRequestHandler):

    def handle(self):
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unpickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handle_log_record(record)

    def unpickle(self, data):
        return pickle.loads(data)

    def handle_log_record(self, record):
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        logger.handle(record)


class Receiver(ThreadingTCPServer):

    allow_reuse_address = True

    def __init__(self,
                 host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=Handler):
        ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def main():
    logging.basicConfig(level='INFO')
    server = Receiver()
    logging.info('%r starting', server)
    server.serve()


if __name__ == '__main__':
    main()
