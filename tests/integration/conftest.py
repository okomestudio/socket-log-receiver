# -*- coding: utf-8 -*-
from typing import Generator

import pytest
from _pytest._py.path import LocalPath
from xprocess import ProcessStarter, XProcess

PROGNAME = "log_receiver"


@pytest.fixture
def receiver(xprocess: XProcess) -> Generator[LocalPath, None, None]:  # type: ignore[no-any-unimported]
    class Starter(ProcessStarter):  # type: ignore
        pattern = r"<.*Receiver.*> starting"
        args = [PROGNAME]

    pid, logpath = xprocess.ensure(PROGNAME, Starter)

    yield logpath

    pinfo = xprocess.getinfo(PROGNAME)
    pinfo.terminate()
