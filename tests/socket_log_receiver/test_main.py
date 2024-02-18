import sys

import pytest

import socket_log_receiver.__main__ as main
from socket_log_receiver.config import config

if sys.version_info >= (3, 6):
    from unittest.mock import patch
else:
    from mock import patch


class TestMain:
    def test_default(self):
        with patch.object(config, "load") as load:
            main.main()

        load.assert_called()

    def test_reload_signal_default(self):
        argv = None  # argv from command-line

        with patch.object(config, "load") as load:
            main.main(argv)

        load.assert_called()

    def test_reload_signal_override(self):
        available_signal = "SIGTERM"
        argv = ["--reload-signal", available_signal]

        with patch.object(config, "load") as load:
            main.main(argv)

        load.assert_called()

    def test_reload_signal_override_with_bad_signal(self):
        bad_signal = "SIGFOO"
        argv = ["--reload-signal", bad_signal]

        with patch.object(config, "load"):
            with pytest.raises(RuntimeError) as exc:
                main.main(argv)

        assert f"Signal '{ bad_signal }' not recognized" in str(exc)
