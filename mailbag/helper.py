import base64
import urllib.parse
from pathlib import Path
import os, shutil, glob
import datetime
from time import time
from bs4 import BeautifulSoup, Doctype
from structlog import get_logger
import mailbag.globals as globals
from mailbag.models import Attachment
import mimetypes
import traceback
import chardet, codecs
from email.header import Header, decode_header, make_header
import http.server
import socketserver
import html

log = get_logger()


def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        log.debug("from: " + str(oldPath))
        log.debug("to: " + str(newPath))
        shutil.move(oldPath, newPath)
    except IOError as e:
        log.error("Unable to move file. %s" % e)


def progress(current, total, start_time, prefix="", suffix="", decimals=1, length=100, fill="█", print_End="\r"):
    """
    Call in a loop to create terminal progress bar

    Parameters:
        current (int): current progress
        total (int): total iterations
        start_time (float): start time
        prefix (String): prefix string
        suffix (String): suffix string
        decimals (int): positive number of decimals in percent complete
        length (int): character length of bar (Int)
        fill (String): bar fill character (Str)
        printEnd (String): end character (e.g. "\r", "\r\n")
    """

    time_spent = time() - start_time
    remaining_time = round(time_spent * (total / current - 1), 2)
    e = datetime.datetime.now()
    percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
    # filledLength = int(length * current // total)
    style = globals.style
    # bar = fill * filledLength + '-' * (length - filledLength)

    dt = f"{e.year}-{e.month:02d}-{e.day:02d} {e.hour:02d}:{e.minute:02d}.{e.second:02d}"
    message_type = f'[{style["cy"][0]}{prefix}{style["b"][1]}]'
    # deco_prefix = f'{style["b"][0]}{prefix}{style["b"][1]}'
    # statusBar = f'|{bar}| {percent}% [{current}MB out of {total}MB] {suffix}'
    status = f"{percent}% [{current} / {total} messages] {remaining_time}s remaining"

    print(f"\r{dt} {message_type} {status}", end=print_End)


def progressMessage(msg, print_End="\r"):
    """
    Shows a message as progress. Useful since it make take awhile to save large bags
    even after all messages have been processed.

    Parameters:
        msg (String): A message to show as progress
    """
    e = datetime.datetime.now()
    style = globals.style
    dt = f"{e.year}-{e.month:02d}-{e.day:02d} {e.hour:02d}:{e.minute:02d}.{e.second:02d}"
    message_type = f'[{style["cy"][0]}{"Progress "}{style["b"][1]}]'
    print(f"\r{dt} {message_type} {msg}", end=print_End)


def processedFile(filePath):
    """
    Add size of this file to counter

    Parameters:
        filePath (String): Location to find the file
    """

    increment = os.path.getsize(filePath) / (1024**2)
    globals.processedSize += increment
    globals.processedSize = round(globals.processedSize, 2)


def getDirectorySize(directory, format):
    """
    Calculate total size of relevant files in the directory

    Parameters:
        directory (String): Location to find files
        format (String): format of the mail type

    Returns:
        String: emailFolder
    """

    filePath = os.path.join(directory, "**", "*." + format)
    total = sum(os.path.getsize(f) for f in glob.iglob(filePath, recursive=True) if os.path.isfile(f))
    total = round(total / (1024**2), 2)
    log.debug(f"Total files to be processed: {total}MB")
    return total


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


def saveAttachments(part):
    return (part.get_filename(), part.get_payload(decode=True))


def deleteFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)


def startServer(dry_run, httpdShared, port=5000):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    log.debug("Starting Server")
    if not dry_run:
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("127.0.0.1", port), QuietHandler) as httpd:
            httpdShared.append(httpd)
            httpd.serve_forever()


def stopServer(dry_run, httpd):
    log.debug("Stopping Server")
    if not dry_run:
        httpd.shutdown()
        httpd.server_close()


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
        if content_disposition != "attachment":
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

                try:
                    message_body = part.get_payload(decode=True).decode(part_encoding)
                except UnicodeDecodeError as e:
                    if enc_source == "read":
                        print("lies!")
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
        header_string (str or None): A as-best-as-we-can-do decoded string
    """
    headerObj, encoding = decode_header(header)[0]
    if encoding:
        # Did we get a real encoding?
        try:
            encoding = codecs.lookup(encoding).name.lower()
        except:
            # If not, might as well try to detect it.
            encoding = chardet.detect(headerObj)["encoding"]
        try:
            header_string = headerObj.decode(encoding)
        except UnicodeDecodeError as e:
            # Document that the header isn't valid
            desc = "Error decoding header with " + encoding
            errors = handle_error(errors, e, desc)
            header_string = headerObj.decode(encoding, errors="replace")
    else:
        # Not encoded
        header_string = headerObj

    return header_string


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


def saveAttachmentOnDisk(dry_run, attachments_dir, message):
    """
    Takes an email message object and writes any attachments in the model
    to the attachments subdirectory according to the mailbag spec

    Parameters:
        dry_run (Boolean): Option to do a test run without writing changes
        attachments_dir (Path): Path to the attachments subdirectory
        message (Email): A full email message object desribed in models.py
    """

    if not dry_run:
        message_attachments_dir = os.path.join(attachments_dir, str(message.Mailbag_Message_ID))
        os.mkdir(message_attachments_dir)

    for attachment in message.Attachments:
        if not attachment.File:
            desc = "Missing attachment content"
            errors = handle_error(errors, None, desc)
        else:
            log.debug("Saving Attachment:" + str(attachment.Name))
            log.debug("Type:" + str(attachment.MimeType))
            if not dry_run:
                attachment_path = os.path.join(message_attachments_dir, attachment.Name)
                f = open(attachment_path, "wb")
                f.write(attachment.File)
                f.close()


def guessMimeType(filename):
    """
    Takes an file name and uses mimetypes to guess the mime type

    Parameters:
        filename (String): Attachment filename

    Returns:
        Mimetype (String)
    """
    return mimetypes.guess_type(filename)[0]


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


def htmlFormatting(message, external_css, headers=True):
    """
    Creates a formatted html file using message text or html body
    inserts any additional styling given by user
    Useful for html and pdf derivative

    Parameters:
        message:message object
        external_css(string): path of css file to customize derivative
        headers(boolean):option to add table of headers

    Returns:
        String: formatted html for pdf, html derivatives
    """

    # check to see which body to use
    html_content = False
    encoding = False
    if message.HTML_Body:
        html_content = message.HTML_Body
        encoding = message.HTML_Encoding
    elif message.Text_Body:
        #  converting text body to html body
        html_content = (
            """
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        #mailbagPlainText{white-space: pre;}
                    </style>
                </head>
                <body>
                    <section id='mailbagPlainText'>"""
            + message.Text_Body
            + """<section>
                </body>
            </html>
        """
        )
        # using utf-8 for ascii plain text bodies as we're adding non-ascii whitespace
        if codecs.lookup(message.Text_Encoding).name.lower() == "ascii":
            log.debug("Using utf-8 to better handle whitespace for plain text ascii body message " + str(message.Mailbag_Message_ID))
            encoding = "utf-8"
        else:
            encoding = message.Text_Encoding
    else:
        log.warn("Unable to format HTML, no message body found for " + str(message.Mailbag_Message_ID))

    if html_content:

        # Formatting HTML with beautiful soup
        soup = BeautifulSoup(html_content.encode(encoding), "html.parser", from_encoding=encoding)

        # Checking if message contains partial html
        if not soup.html:
            html_content = "<html>" + html_content + "</html>"
            soup = BeautifulSoup(html_content.encode(encoding), "html.parser", from_encoding=encoding)
        if not soup.head:
            head = soup.new_tag("head")
            soup.html.insert(0, head)
        if not soup.body:
            body = soup.new_tag("body")
            soup.head.next_element.wrap(body)

        # Check Doctype
        doctype = False
        for item in soup.contents:
            if isinstance(item, Doctype):
                doctype = True
        if doctype is False:
            tag = Doctype("html")
            soup.insert(0, tag)

        # optionally adds headers table to html
        if headers:
            # Make headers table
            table = "<table id='mailbagHeadersTable'>"
            if message.Subject:
                h2 = "<h2>" + message.Subject + "</h2>"
            else:
                h2 = ""
            # Headers to display
            headerFields = [
                "Mailbag_Message_ID",
                "Message_ID",
                "From",
                "Date",
                "To",
                "Cc",
                "Bcc",
                "Subject",
            ]
            # Getting the values of the attrbutes and appending to HTML string
            for headerField in headerFields:
                value = getattr(message, headerField)
                if not value is None and value != []:
                    table += "<tr>"
                    table += "<td class='header'>" + str(headerField) + "</td>"
                    table += "<td>" + str(getattr(message, headerField)).replace("<", "&lt;").replace(">", "&gt;") + "</td>"
                    table += "</tr>"
            if len(message.Attachments) > 0:
                attachmentNumber = len(message.Attachments)
                table += "<tr>"
                table += "<td class='header'>Attachments</td><td>"
                for i, attachment in enumerate(message.Attachments):
                    table += attachment.Name
                    if i + 1 < attachmentNumber:
                        table += "<br/>"
                table += "</td>"
                table += "</tr>"
            tableSection = "<section id='mailbagHeaders'>" + h2 + table + "</table></section>"
            soupTable = BeautifulSoup(tableSection, "html.parser")

            # Add headers table to HTML body
            soup.body.insert(0, soupTable)

        # Embedding Encoding with meta
        meta = soup.new_tag("meta")
        meta["charset"] = "utf-8"
        soup.head.insert(0, meta)

        # Embedding default styling
        default_css = """
            @media print {
                /* for Chrome margins */
                @page { margin: 10; }
            }
            section#mailbagHeaders table#mailbagHeadersTable {
                width: 100%;
                margin-bottom: 35px;
                text-align: left;
                border-top: 4px solid #000000;
                padding-top: 8px;
                border-collapse: separate;
                border-spacing: 0 1px;
            }
            section#mailbagHeaders table#mailbagHeadersTable > tbody > tr > td {
                font: 16px Arial sans-serif;
                color:  #000000;
                padding: 2px 5px;
            }
            section#mailbagHeaders table#mailbagHeadersTable tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            section#mailbagHeaders h2 {
                margin-bottom: 2px;
                font-size: 24px;
                font-family: Arial sans-serif;
        """
        style = soup.new_tag("style")
        style.string = default_css
        soup.head.append(style)

        # Adding external_css
        if external_css:
            link = soup.new_tag("link")
            link["rel"] = "stylesheet"
            link["type"] = "text/css"
            link["href"] = "file:///" + external_css
            soup.head.append(link)

        # Embedding Images
        # HT to extract_msg for this approach
        # https://github.com/TeamMsgExtractor/msg-extractor/blob/6bed8213de1a7a41739fcf5c9363322508711fce/extract_msg/message_base.py#L403-L414
        tags = (tag for tag in soup.findAll("img") if tag.get("src") and tag.get("src").startswith("cid:"))
        data = None
        for tag in tags:
            # Iterate through the attachments until we get the right one.
            cid = tag["src"][4:]

            for attachment in message.Attachments:
                if attachment.Name in cid:
                    data = attachment.File

            # If we found anything, inject it.
            if data:
                tag["src"] = (b"data:image;base64," + base64.b64encode(data)).decode(encoding)

        html_content = soup.prettify(encoding).decode(encoding)

    return html_content, encoding
