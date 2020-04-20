import sys

import socket_log_receiver.__main__ as main
from socket_log_receiver.config import config

if sys.version_info >= (3, 6):
    from unittest.mock import patch
else:
    from mock import patch


class TestMain:
    def test(self):
        with patch.object(config, "load") as load:
            main.main()
            load.assert_called()
