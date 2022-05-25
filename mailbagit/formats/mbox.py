import email
import mailbox

from structlog import get_logger
from pathlib import Path
import os, shutil
import email.errors

from mailbagit.email_account import EmailAccount
from mailbagit.models import Email, Attachment
import mailbagit.helper.format as format
import mailbagit.helper.common as common
import platform

log = get_logger()


class Mbox(EmailAccount):
    """Mbox - This concrete class parses mbox file format"""

    format_name = "mbox"
    format_agent = mailbox.__name__
    format_agent_version = platform.python_version()

    def __init__(self, target_account, args, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.path = target_account
        self.dry_run = args.dry_run
        self.mailbag_name = args.mailbag_name
        self.companion_files = args.companion_files
        self.iteration_only = False
        log.info("Reading : ", Path=self.path)

    def account_data(self):
        return account_data

    def messages(self):

        companion_files = []
        if os.path.isfile(self.path):
            parent_dir = os.path.dirname(self.path)
            fileList = [self.path]
        else:
            parent_dir = self.path
            fileList = []
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    mailbag_path = os.path.join(self.path, self.mailbag_name) + os.sep
                    fileRoot = root + os.sep
                    # don't count the newly-created mailbag
                    if not fileRoot.startswith(mailbag_path):
                        if file.lower().endswith("." + self.format_name):
                            fileList.append(os.path.join(root, file))
                        elif self.companion_files:
                            companion_files.append(os.path.join(root, file))

        for filePath in fileList:
            rel_path = format.relativePath(self.path, filePath)
            if len(rel_path) < 1:
                originalFile = Path(filePath).name
            else:
                originalFile = Path(os.path.normpath(rel_path)).as_posix()
            # original file is now the relative path to the MBOX from the provided path

            data = mailbox.mbox(filePath)
            for mail in data.itervalues():

                if self.iteration_only:
                    yield None
                    continue

                attachments = []
                errors = {}
                errors["msg"] = []
                errors["stack_trace"] = []

                try:
                    mailObject = email.message_from_bytes(mail.as_bytes(), policy=email.policy.default)

                    # Try to parse content
                    try:
                        bodies = {}
                        bodies["html_body"] = None
                        bodies["text_body"] = None
                        bodies["html_encoding"] = None
                        bodies["text_encoding"] = None
                        if mailObject.is_multipart():
                            for part in mailObject.walk():
                                bodies, attachments, errors = format.parse_part(part, bodies, attachments, errors)
                        else:
                            bodies, attachments, errors = format.parse_part(mailObject, bodies, attachments, errors)
                    except Exception as e:
                        desc = "Error parsing message parts"
                        errors = common.handle_error(errors, e, desc)

                    # Look for message arrangement
                    try:
                        messagePath = Path(format.messagePath(mailObject)).as_posix()
                        if messagePath == ".":
                            messagePath = ""
                        derivativesPath = Path(os.path.splitext(originalFile)[0], format.normalizePath(messagePath)).as_posix()
                    except Exception as e:
                        desc = "Error reading message path from headers"
                        errors = common.handle_error(errors, e, desc)

                    message = Email(
                        Error=errors["msg"],
                        Message_ID=format.parse_header(mail["Message-ID"]),
                        Original_File=originalFile,
                        Message_Path=messagePath,
                        Derivatives_Path=derivativesPath,
                        Date=format.parse_header(mail["Date"]),
                        From=format.parse_header(mail["From"]),
                        To=format.parse_header(mail["To"]),
                        Cc=format.parse_header(mail["Cc"]),
                        Bcc=format.parse_header(mail["Bcc"]),
                        Subject=format.parse_header(mail["Subject"]),
                        Content_Type=mailObject.get_content_type(),
                        Headers=mail,
                        HTML_Body=bodies["html_body"],
                        HTML_Encoding=bodies["html_encoding"],
                        Text_Body=bodies["text_body"],
                        Text_Encoding=bodies["text_encoding"],
                        Message=mailObject,
                        Attachments=attachments,
                        StackTrace=errors["stack_trace"],
                    )
                except (email.errors.MessageParseError, Exception) as e:
                    desc = "Error parsing message"
                    errors = common.handle_error(errors, e, desc)
                    message = Email(Error=errors["msg"], StackTrace=errors["stack_trace"])

                yield message

            # Make sure the MBOX file is closed
            data.close()
            # Move MBOX to new mailbag directory structure
            if not self.iteration_only:
                new_path = format.moveWithDirectoryStructure(self.dry_run, parent_dir, self.mailbag_name, self.format_name, filePath)

        if self.companion_files:
            # Move all files into mailbag directory structure
            for companion_file in companion_files:
                new_path = format.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, companion_file)
