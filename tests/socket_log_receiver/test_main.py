import socket_log_receiver.__main__ as main

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestMain:
    def test(self):
        with patch("socket_log_receiver.__main__.Receiver.serve") as serve:
            main.main()
            serve.assert_called()
