import signal
from unittest.mock import patch

import pytest
import socket_log_receiver.__main__ as main
from socket_log_receiver import config


class TestMain:
    def test_default(self) -> None:
        with patch("socket_log_receiver.receivers.Receiver.serve") as serve:
            main.main()

        serve.assert_called()

    def test_reload_signal_default(self) -> None:
        argv = None  # argv from command-line

        with patch("socket_log_receiver.receivers.Receiver.serve"):
            main.main(argv)

        assert signal.getsignal(signal.SIGHUP) == config.reloader

    def test_reload_signal_override(self) -> None:
        available_signal = "SIGTERM"
        argv = ["--reloader-signal", available_signal]

        with patch("socket_log_receiver.receivers.Receiver.serve"):
            main.main(argv)

        assert signal.getsignal(signal.SIGTERM) == config.reloader

    def test_reload_signal_override_with_bad_signal(self) -> None:
        bad_signal = "SIGFOO"
        argv = ["--reloader-signal", bad_signal]

        with patch("socket_log_receiver.receivers.Receiver.serve"):
            with pytest.raises(RuntimeError) as exc:
                main.main(argv)

        assert f"Signal '{ bad_signal }' not recognized" in str(exc)
