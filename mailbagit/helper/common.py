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
        error_msg = level.upper() + ": " + desc + ": " + repr(exception)
        stack_header = (
            "**************************************************************************\n"
            + error_msg
            + "\n**************************************************************************\n"
        )
        errors["stack_trace"].append(stack_header + traceback.format_exc())
    else:
        error_msg = level.upper() + ": " + desc + "."
        errors["stack_trace"].append(desc + ".")
    errors["msg"].append(error_msg)

    print()
    log_msg = (error_msg[:150] + "..") if len(error_msg) > 150 else error_msg
    if level == "warn":
        log.warn(log_msg)
    else:
        log.error(log_msg)

    return errors
