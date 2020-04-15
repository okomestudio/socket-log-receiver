import pickle
import sys
from logging.handlers import SocketHandler

import pytest
from socket_log_receiver.receivers import Receiver
from socket_log_receiver.receivers import _Handler

if sys.version_info >= (3, 6):
    from unittest.mock import MagicMock, Mock, patch
else:
    from mock import MagicMock, Mock, patch


@pytest.fixture
def handler(response, server):
    return _Handler(response, "localhost:9999", server)


class TestHandler:
    def test_handle(self, record, response, server):
        sh = SocketHandler("localhost", "9999")
        stream = sh.makePickle(record)

        def recv(n):
            # TODO: Can use nonlocal on Python 3
            idx = recv.idx
            s = stream[idx : idx + n]
            recv.idx += n
            return s

        recv.idx = 0

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


@pytest.mark.skip(reason="errors on OSError: [Errno 98] Address already in use")
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
