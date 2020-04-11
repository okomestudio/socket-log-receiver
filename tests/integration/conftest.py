# -*- coding: utf-8 -*-
import pytest
from xprocess import ProcessStarter

PROGNAME = "log_receiver"


@pytest.fixture
def receiver(xprocess):
    class Starter(ProcessStarter):
        pattern = r"<.*Receiver.*> starting"
        args = [PROGNAME]

    pid, logpath = xprocess.ensure(PROGNAME, Starter)

    yield logpath

    pinfo = xprocess.getinfo(PROGNAME)
    pinfo.terminate()
