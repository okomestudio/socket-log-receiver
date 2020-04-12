import sys

import socket_log_receiver.__main__ as main

if sys.version_info >= (3, 6):
    from unittest.mock import patch
else:
    from mock import patch


class TestMain:
    def test(self):
        with patch("socket_log_receiver.__main__.Receiver.serve") as serve:
            main.main()
            serve.assert_called()
