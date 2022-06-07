import traceback
from mailbagit.models import Error
from structlog import get_logger

log = get_logger()


def handle_error(errors, exception, desc, level="error"):
    """
    Is called when an exception is raised in the parsers, helpers, or derivatives.
    Takes a list, creates an Error object, and returns the list with the Error object appended.
    Messages can have multiple error objects, so this may be called multiple times per message

    Parameters:
        errors (List): List of Error objects defined in models.py
        exception (Exception): The exception raised
        desc (String): A full email message object desribed in models.py
        level (String): Whether to log as error or warn. Defaults to error.
    Returns:
        errors (List): List of Error objects defined in models.py
    """
    if exception:
        error_msg = desc + ": " + repr(exception)
        stack_header = (
            "**************************************************************************\n"
            + level.upper()
            + ": "
            + error_msg
            + "\n**************************************************************************\n"
        )
        stack_trace = stack_header + traceback.format_exc()
    else:
        error_msg = desc + "."
        stack_trace = level.upper() + ": " + desc + "."

    # print()
    log_msg = (error_msg[:150] + "..") if len(error_msg) > 150 else error_msg
    if level == "warn":
        log.warn(log_msg)
    else:
        log.error(log_msg)

    errorObj = Error(
        Level=level,
        Description=level.upper() + ": " + error_msg,
        StackTrace=stack_trace,
    )
    errors.append(errorObj)

    return errors
