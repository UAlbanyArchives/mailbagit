import os, shutil, glob
from pathlib import Path
import mimetypes
import urllib.parse
import chardet, codecs
from email.header import Header, decode_header, make_header
from mailbagit.models import Attachment

from structlog import get_logger

log = get_logger()


def relativePath(mainPath, file):
    """
    Gets the relative path of an input file within the input directory structure
    Useful for getting the path of messages within an email account

    Parameters:
        mainPath (String): Parent or provided directory path
        file (String): Email file path

    Returns:
        String: emailFolder
    """

    fullPath = Path(mainPath).resolve()
    fullFilePath = Path(file).resolve()
    relPath = str(fullFilePath.relative_to(fullPath))
    if relPath == ".":
        return ""
    else:
        return relPath


def parse_part(part, bodies, attachments, errors):
    """
    Used for EML and MBOX parsers
    Parses a part of an email message for multipart messages or a full message with a single part

    Parameters:
        part (email.Message.message part):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        bodies (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        attachments (list): a list of attachment object as defined in models.py
        errors (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
    Returns:
        bodies (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        attachments (list): a list of attachment object as defined in models.py
        errors (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
    """
    content_type = part.get_content_type()
    content_disposition = part.get_content_disposition()

    # Extract body
    try:
        if content_disposition != "attachment" and content_disposition != "inline":
            if content_type == "text/html" or content_type == "text/plain":
                part_encoding = part.get_content_charset()
                enc_source = "read"
                if part_encoding:
                    try:
                        part_encoding = codecs.lookup(part_encoding).name.lower()
                    except:
                        part_encoding = chardet.detect(part.get_payload(decode=True))["encoding"]
                        enc_source = "detected"
                else:
                    part_encoding = chardet.detect(part.get_payload(decode=True))["encoding"]
                    enc_source = "detected"

                try:
                    message_body = part.get_payload(decode=True).decode(part_encoding)
                except UnicodeDecodeError as e:
                    if enc_source == "read":
                        # lies!
                        detected_encoding = chardet.detect(part.get_payload(decode=True))["encoding"]
                        try:
                            message_body = part.get_payload(decode=True).decode(detected_encoding)
                            desc = (
                                "Failed to decode message body with listed encoding "
                                + part_encoding
                                + " (lies!), but successfully decoded with detected encoding "
                                + detected_encoding
                            )
                            errors = handle_error(errors, e, desc, "warn")
                            part_encoding = detected_encoding
                        except UnicodeDecodeError as e:
                            desc = "Error decoding message body with " + part_encoding + " (" + enc_source + ")"
                            errors = handle_error(errors, e, desc)
                            message_body = part.get_payload(decode=True).decode(part_encoding, errors="replace")
                    else:
                        desc = "Error decoding message body with " + part_encoding + " (" + enc_source + ")"
                        errors = handle_error(errors, e, desc)
                        message_body = part.get_payload(decode=True).decode(part_encoding, errors="replace")

                if content_type == "text/html":
                    bodies["html_encoding"] = part_encoding
                    bodies["html_body"] = message_body
                elif content_type == "text/plain":
                    bodies["text_encoding"] = part_encoding
                    bodies["text_body"] = message_body
    except Exception as e:
        desc = "Error parsing message body"
        errors = handle_error(errors, e, desc)

    # Extract attachments
    if part.get_content_maintype() == "multipart":
        pass
    elif content_disposition is None:
        pass
    else:
        try:
            if not part.get_payload(decode=True):
                if part.get_filename():
                    desc = "Missing attachment content, failed to read attachment " + part.get_filename()
                else:
                    desc = "Missing attachment content and filename, failed to read attachment"
                errors = handle_error(errors, None, desc)
            else:
                attachmentFile = part.get_payload(decode=True)
                if part.get_filename():
                    attachmentName = part.get_filename()
                else:
                    desc = "Missing attachment name, using integer"
                    errors = handle_error(errors, None, desc)
                    attachmentName = str(len(attachments))

                attachment = Attachment(
                    Name=attachmentName,
                    File=attachmentFile,
                    MimeType=content_type,
                )
                attachments.append(attachment)
        except Exception as e:
            desc = "Error parsing attachments"
            errors = handle_error(errors, e, desc)

    return bodies, attachments, errors


def decode_header_part(header):
    """
    Used for to decode strings according to RFC 1342.
    If the string is not encoded, just return it.
    For encoded strings it tries to decode it with email.header.decode_header().
    If we don't get a real encoding, it tries it best to detect it.
    Errors are logged and documented in the error report.

    Parameters:
        header (email.header.Header or string or None):
    Returns:
        header_string (str): A as-best-as-we-can-do decoded string
    """
    # headerObj, encoding = decode_header(header)[0]
    header_string = []
    for part in decode_header(header):
        headerObj, encoding = part
        if encoding:
            # Did we get a real encoding?
            try:
                encoding = codecs.lookup(encoding).name.lower()
            except:
                # If not, might as well try to detect it.
                encoding = chardet.detect(headerObj)["encoding"]
            try:
                header_string.append(headerObj.decode(encoding))
            except UnicodeDecodeError as e:
                # Document that the header isn't valid
                desc = "Error decoding header with " + encoding
                errors = handle_error(errors, e, desc)
                header_string.append(headerObj.decode(encoding, errors="replace"))
        else:
            if isinstance(headerObj, str):
                # Not encoded
                header_string.append(headerObj)
            else:
                # Oddly, there are weird cases where quotes (") return a binary with no encoding.
                # Dunno what to do here so just hopefully safely decode it?
                header_string.append(headerObj.decode(errors="replace"))

    return "".join(header_string)


def parse_header(header):
    """
    Used to handle headers that have RFC 1342 encoding.
    Sometimes the whole header is encoded, while
    sometimes only part of the header string is encoded.
    In some cases we also get a Header object that
    decode_header_part() also handles.

    Parameters:
        header (email.header.Header or string or None):
    Returns:
        header_string (str or None): A as-best-as-we-can-do decoded string
    """
    if header is None:
        header_string = None
    else:
        if isinstance(header, str):
            header_list = []
            for header_part in header.split(" "):
                header_list.append(decode_header_part(header_part))
            header_string = " ".join(header_list)
        else:
            header_string = html.unescape(decode_header_part(header))

    return header_string


def messagePath(headers):
    """
    Tries to read any email folder arragement from headers
    Useful for getting the path of messages within an email account

    Parameters:
        headers (email.message.Message): Can be used as a dict of email headers

    Returns:
        String: messagePath (must at least return an empty string)
    """

    if headers["X-Folder"]:
        messagePath = Path(headers["X-Folder"]).as_posix()
    else:
        messagePath = ""
    return messagePath


def normalizePath(path):
    # this is not sufficent yet
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
            else:
                new_path.append(name)
        out_path = Path(os.path.join(*new_path)).as_posix()
    else:
        out_path = path

    if out_path == ".":
        return ""
    else:
        return out_path


def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        log.debug("from: " + str(oldPath))
        log.debug("to: " + str(newPath))
        shutil.move(oldPath, newPath)
    except IOError as e:
        log.error("Unable to move file. %s" % e)


def getFileBeforeAfterPath(mainPath, mailbag_name, input, file):
    """
    Creates file paths for input mail files and new paths

    Parameters:
        mainPath (String) :
        mailbag_name (String) :
        input (String) :
        file (String) :
    """
    fullPath = Path(mainPath).resolve()
    fullFilePath = Path(file).resolve()
    relPath = fullFilePath.relative_to(fullPath).parents[0]
    filename = fullFilePath.name
    folder_new = os.path.join(fullPath, mailbag_name, "data", input)
    file_new_path = os.path.join(folder_new, relPath, filename)

    return fullPath, fullFilePath, file_new_path, relPath


def moveWithDirectoryStructure(dry_run, mainPath, mailbag_name, input, file):
    """
    Create new mailbag directory structure while maintaining the input data's directory structure.
    Useful for MBOX, EML, and MSG files.

    Parameters:
        dry_run (Boolean):
        mainPath (String): Parent or provided directory path
        mailbag_name (String): Mailbag name
        input (String): Mail type
        emailFolder (String): Path of the email export file relative to mainPath
        file (String): Email file path

    Returns:
        file_new_path (Path): The path where the file was moved
    """

    fullPath, fullFilePath, file_new_path, relPath = getFileBeforeAfterPath(mainPath, mailbag_name, input, file)
    log.debug("Moving: " + str(fullFilePath) + " to: " + str(file_new_path) + " SubFolder: " + str(relPath))

    if not dry_run:
        moveFile(dry_run, fullFilePath, file_new_path)
        # clean up old directory structure
        p = fullFilePath.parents[0]
        while p != p.root and p != fullPath:
            if not os.listdir(p):
                log.debug("Cleaning: " + str(p))
                os.rmdir(p)
                # dirty hack since rmdir is not synchronous on Windows
                if os.name == "nt":
                    import time

                    time.sleep(0.01)
            p = p.parent

    return file_new_path


def guessMimeType(filename):
    """
    Takes an file name and uses mimetypes to guess the mime type

    Parameters:
        filename (String): Attachment filename

    Returns:
        Mimetype (String)
    """
    return mimetypes.guess_type(filename)[0]
