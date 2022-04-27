import os
import logging, structlog


def configure():

    log = structlog.get_logger()

    LOGLEVEL = "WARN"
    try:
        LOGLEVEL = os.environ.get("MAILBAG_LOG_LEVEL", None).upper()
    except:
        log.warn("MAILBAG_LOG_LEVEL environment variable not set or incorrect")
    level = logging._nameToLevel[LOGLEVEL]

    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))
    log = structlog.get_logger()
    log.info("MAILBAG_LOG_LEVEL:", LOGS=LOGLEVEL)
