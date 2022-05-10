import traceback

from structlog import get_logger
log = get_logger()

def handle_error(errors, exception, desc, level="error"):
    """
    Is called when an exception is raised in the parsers.
    returns a dict of readable and full trace errors that can be appended to.

    Parameters:
        errors (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        exception (Exception): The exception raised
        desc (String): A full email message object desribed in models.py
        level (String): Whether to log as error or warn. Defaults to error.
    Returns:
        errors (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
    """
    if exception:
        error_msg = desc + ": " + repr(exception)
        errors["stack_trace"].append(traceback.format_exc())
    else:
        error_msg = desc + "."
        errors["stack_trace"].append(desc + ".")
    errors["msg"].append(error_msg)

    print()
    if level == "warn":
        log.warn(error_msg)
    else:
        log.error(error_msg)

    return errors

