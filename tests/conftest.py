# -*- coding: utf-8 -*-
import pytest
from xprocess import ProcessStarter


@pytest.fixture
def receiver(xprocess):
    class Starter(ProcessStarter):
        pattern = r"<.*Receiver.*> starting"
        args = ["receiver"]

    pid, logpath = xprocess.ensure("receiver", Starter)

    yield logpath

    pinfo = xprocess.getinfo("receiver")
    pinfo.terminate()
