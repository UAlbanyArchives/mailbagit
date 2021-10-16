import os
from dotenv import load_dotenv, find_dotenv
import logging
import structlog

def configure():
    load_dotenv(find_dotenv())
    DEBUG=os.getenv('DEBUG').lower()
    if DEBUG=='true':
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )
    else:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )
    log = structlog.get_logger()
    log.info("MODE:", DEBUG=DEBUG)
