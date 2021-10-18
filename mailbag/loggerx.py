import os
import logging, structlog


def configure():
    
    log = structlog.get_logger()
    
    try:
        LOGLEVEL = os.environ.get('MAILBAG_LOG_LEVEL', None).upper()
        level = logging._nameToLevel[LOGLEVEL]
    except:
        log.warn("MAILBAG_LOG_LEVEL environment variable not set or incorrect")
        
    structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(level)
            )
    log = structlog.get_logger()
    log.info("MAILBAG_LOG_LEVEL:", LOGS=LOGLEVEL)
