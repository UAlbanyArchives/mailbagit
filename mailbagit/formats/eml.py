import datetime
import json
from pathlib import Path
import mailbagit.helper.format as format
import mailbagit.helper.common as common
from mailbagit.loggerx import get_logger
from email import parser
from mailbagit.email_account import EmailAccount
from mailbagit.models import Email, Attachment
import email
import os
import platform

log = get_logger()


class EML(EmailAccount):
    """EML - This concrete class parses eml file format"""

    format_name = "eml"
    format_agent = email.__name__
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

        fileList = []
        companion_files = []
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

            if self.iteration_only:
                yield None
                continue

            originalFile = Path(format.relativePath(self.path, filePath)).as_posix()

            attachments = []
            errors = []
            try:
                with open(filePath, "rb") as f:
                    msg = email.message_from_binary_file(f, policy=email.policy.default)

                    try:
                        # Parse message bodies
                        bodies = {}
                        bodies["html_body"] = None
                        bodies["text_body"] = None
                        bodies["html_encoding"] = None
                        bodies["text_encoding"] = None
                        if msg.is_multipart():
                            for part in msg.walk():
                                bodies, attachments, errors = format.parse_part(part, bodies, attachments, errors)
                        else:
                            bodies, attachments, errors = format.parse_part(msg, bodies, attachments, errors)

                    except Exception as e:
                        desc = "Error parsing message parts"
                        errors = common.handle_error(errors, e, desc)

                    # Look for message arrangement
                    try:
                        messagePath = Path(format.messagePath(msg)).as_posix()
                        if messagePath == ".":
                            messagePath = ""
                        unsafePath = os.path.join(os.path.dirname(originalFile), messagePath)
                        derivativesPath = format.normalizePath(unsafePath)
                    except Exception as e:
                        desc = "Error reading message path from headers"
                        errors = common.handle_error(errors, e, desc)

                    message = Email(
                        Errors=errors,
                        Message_ID=format.parse_header(msg["message-id"]),
                        Original_File=originalFile,
                        Message_Path=messagePath,
                        Derivatives_Path=derivativesPath,
                        Date=format.parse_header(msg["date"]),
                        From=format.parse_header(msg["from"]),
                        To=format.parse_header(msg["to"]),
                        Subject=format.parse_header(msg["subject"]),
                        Content_Type=msg.get_content_type(),
                        Headers=msg,
                        HTML_Body=bodies["html_body"],
                        HTML_Encoding=bodies["html_encoding"],
                        Text_Body=bodies["text_body"],
                        Text_Encoding=bodies["text_encoding"],
                        Message=msg,
                        Attachments=attachments,
                    )

            except (email.errors.MessageParseError, Exception) as e:
                desc = "Error parsing message"
                errors = common.handle_error(errors, e, desc)
                message = Email(Errors=errors)

            # Move EML to new mailbag directory structure
            yield message
            new_path = format.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, filePath)

        if self.companion_files:
            # Move all files into mailbag directory structure
            for companion_file in companion_files:
                new_path = format.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, companion_file)
