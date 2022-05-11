---
layout: page
title: Configuring Logging
permalink: /logging/
parent: Using mailbagit
nav_order: 3
---

# Configuring Logging

* The level of logs displayed by Mailbag is based on an environment variable `MAILBAG_LOG_LEVEL`.

* Log levels are available in the following order : `NOTSET`, `DEBUG`, `INFO`, `WARN`, `ERROR`, and `CRITICAL`.
For example, when the `MAILBAG_LOG_LEVEL` is `DEBUG`, `Mailbag` displays logs of all levels.
And when `MAILBAG_LOG_LEVEL` is `WARN`, it displays logs of level `WARN` and above. i.e. `WARN`, `ERROR`, or `CRITICAL`.

* If no `MAILBAG_LOG_LEVEL` environment variable is set, mailbag will default to `WARN`.

Unix example:

```
export MAILBAG_LOG_LEVEL=info
echo $MAILBAG_LOG_LEVEL
> info
```

Windows Powershell example:

```
$env:MAILBAG_LOG_LEVEL='debug'
$env:MAILBAG_LOG_LEVEL
> debug
```

On Windows, you can also [set environment variables by searching "edit environment variable"](https://www.onmsft.com/how-to/how-to-set-an-environment-variable-in-windows-10).



### Example of the logger initiation and usage in `Python`:

```
from structlog import get_logger
import mailbag.loggerx
loggerx.configure()
log = get_logger()	
log.error("Error message here")
log.info("Information message here")
```