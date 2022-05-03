import os
import logging, structlog
import mailbag.globals as globals

def configure():
    
    log = structlog.get_logger()
    
    globals.log_level = "WARN"
    try:
        globals.log_level = os.environ.get('MAILBAG_LOG_LEVEL', None).upper()
    except:
        log.warn("MAILBAG_LOG_LEVEL environment variable not set or incorrect")
    level = logging._nameToLevel[globals.log_level]
        
    structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(level)
            )
    log = structlog.get_logger()
    log.info("MAILBAG_LOG_LEVEL:", LOGS=globals.log_level)
