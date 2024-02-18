# -*- coding: utf-8 -*-
from typing import Any, Generator

import pytest
from _pytest._py.path import LocalPath
from xprocess import ProcessStarter

PROGNAME = "log_receiver"


@pytest.fixture
def receiver(xprocess: Any) -> Generator[LocalPath, None, None]:
    class Starter(ProcessStarter):  # type: ignore
        pattern = r"<.*Receiver.*> starting"
        args = [PROGNAME]

    pid, logpath = xprocess.ensure(PROGNAME, Starter)

    yield logpath

    pinfo = xprocess.getinfo(PROGNAME)
    pinfo.terminate()
