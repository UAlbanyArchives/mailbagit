import os
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


def normalizePath(path):
    """
    Is called to normalize paths on windows to make sure they are valid.
    It uses urllib.parse.quote_plus() to URL escape invalid characters

    Parameters:
        path (str): Unsafe path/to/stuff
    Returns:
        out_path (str): Safe path/to/stuff
    """
    if os.name == "nt":
        specials = ["<", ">", ":", '"', "/", "|", "?", "*"]
        special_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        new_path = []
        for name in os.path.normpath(path).split(os.sep):
            illegal = False
            for char in specials:
                if char in name:
                    illegal = True
            if illegal:
                new_path.append(urllib.parse.quote_plus(name))
            elif name.upper() in special_names:
                new_path.append("~" + name + "~")
            else:
                new_path.append(name)
        out_path = Path(os.path.join(*new_path)).as_posix()
    else:
        out_path = path

    if out_path == ".":
        return ""
    else:
        return out_path
