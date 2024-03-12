[![License](https://img.shields.io/pypi/l/socket-log-receiver.svg)](https://pypi.org/project/socket-log-receiver/)
[![PyPI Version](https://badge.fury.io/py/socket-log-receiver.svg)](https://pypi.org/project/socket-log-receiver/)
[![Package Status](https://img.shields.io/pypi/status/socket-log-receiver.svg)](https://pypi.org/project/resconfig/)
[![pyversion Status](https://img.shields.io/pypi/pyversions/socket-log-receiver.svg)](https://img.shields.io/pypi/pyversions/socket-log-receiver.svg)
[![CircleCI](https://circleci.com/gh/okomestudio/socket-log-receiver.svg?style=shield)](https://circleci.com/gh/okomestudio/socket-log-receiver)
[![Coverage Status](https://coveralls.io/repos/github/okomestudio/socket-log-receiver/badge.svg?branch=development)](https://coveralls.io/github/okomestudio/socket-log-receiver?branch=development&kill_cache=1)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


# Socket Log Receiver

`socket_log_receiver` is a light-weight socket log receiving server.
The server aggregates messages from multi-process applications via a
socket and logs them to a single file. The service is used with
Python's stdlib `logging` package, which by default does not support
multi-process writes to a single file.


## Installation

``` shell
$ pip install socket-log-receiver
```


## Basic Usage

The receiver service should be run as a service:

``` shell
$ python -m socket_log_receiver  # as a module
$ log_receiver                   # as a command-line program
```

These are equivalent.

By default, the receiver service starts listening on `localhost:9020`.
These can be changed through CLI options; see the Help section below.

In the application, use `SocketHandler` to send logs to the receiver
service.

``` python
from logging.handlers import SocketHandler

handler = SocketHandler('localhost', 9020)  # handler to send logs to localhost:9020
logging.root.addHandler(handler)            # add the socket handler to the root logger
```

This way, the root logger sends logging messages to the receiver service.

### Help

``` shell
$ python -m socket_log_receiver -h
$ log_receiver -h
```

### Undefined Signal

The receiver service's configuration is managed by
[resconfig](https://github.com/okomestudio/resconfig). By default, the
dynamic configuration update is trigged by `SIGHUP`. Some systems
might not make this signal available, in which case you could use a
different signal for the trigger using the command-line option, e.g.

``` shell
$ log_receiver --reloader-signal SIGUSR2
```


## Development

``` shell
$ pip install -e .[dev]
$ pre-commit install
```


### Running Tests

``` shell
$ pip install -e .[test]
$ pytest
```
