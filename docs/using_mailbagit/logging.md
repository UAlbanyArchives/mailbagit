---
layout: page
title: Configuring Logging
permalink: /logging/
parent: Using mailbagit
nav_order: 4
---

# Configuring Logging

## Log Levels

* The level of logs displayed by `mailbagit` is based on an environment variable `MAILBAGIT_LOG_LEVEL`.

* Log levels are available in the following order : `NOTSET`, `DEBUG`, `INFO`, `WARN`, `ERROR`, and `CRITICAL`.
For example, when the `MAILBAGIT_LOG_LEVEL` is `DEBUG`, `mailbagit` displays logs of all levels.
And when `MAILBAGIT_LOG_LEVEL` is `WARN`, it displays logs of level `WARN` and above. i.e. `WARN`, `ERROR`, or `CRITICAL`.

* If no `MAILBAGIT_LOG_LEVEL` environment variable is set, `mailbagit` will default to `WARN`.

Unix example:

```
export MAILBAGIT_LOG_LEVEL=info
echo $MAILBAGIT_LOG_LEVEL
> info
```

Windows Powershell example:

```
$env:MAILBAGIT_LOG_LEVEL='debug'
$env:MAILBAGIT_LOG_LEVEL
> debug
```

On Windows, you can also [set environment variables by searching "edit environment variable"](https://www.onmsft.com/how-to/how-to-set-an-environment-variable-in-windows-10).


## Log Output

By default, `mailbagit` streams human-readable logs to `stdout`. You may also use the `--log` argument to also send the logs to a file:

```
mailbagit path/to/account.mbox -i mbox -d pdf warc -m test_mailbag --log path/to/file.log
```

For more structured logging, you may also use `-j` or `--log-json` to format the logs as [line delimined JSON](https://jsonlines.org/):

```
mailbagit path/to/account.pst -i pst -d warc eml -m test_mailbag --log-json

> {"message": "Reading: .\\path\\account.pst", "logger": "mailbagit", "level": "info", "timestamp": "2022-07-06T00:47:38.295203Z"}
> {"message": "Found 331 messages.", "logger": "mailbagit", "level": "info", "timestamp": "2022-07-06T00:47:39.429532Z"}
> {"message": "Writing CSV reports...", "logger": "mailbagit", "level": "info", "timestamp": "2022-07-06T00:47:50.568199Z"}
> {"message": "Finished packaging mailbag.", "logger": "mailbagit", "level": "info", "timestamp": "2022-07-06T00:47:50.568199Z"}
```


## Example of the logger initiation and usage as a library:

```
from mailbagit.loggerx import get_logger

logging.setup_logging(filename='my_cool_logfile.log')
log = get_logger()


# do stuff
logger.info("my_event_name", property1="a property", anything={"json": "serializable"}))
# do more stuff
```
