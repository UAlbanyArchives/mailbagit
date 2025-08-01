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
from itertools import chain

log = get_logger()


class EML(EmailAccount):
    """EML - This concrete class parses eml file format"""

    format_name = "eml"
    format_agent = email.__name__
    format_agent_version = platform.python_version()

    def __init__(self, args, source_parent_dir, mailbag_dir, mailbag_name, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        self._account_data = {}

        self.path = args.path
        self.dry_run = args.dry_run
        self.keep = args.keep
        self.mailbag_name = mailbag_name
        self.mailbag_dir = mailbag_dir
        self.source_parent_dir = source_parent_dir
        self.companion_files = args.companion_files

        log.info("Reading: " + self.path)

    @property
    def account_data(self):
        return self._account_data

    @property
    def number_of_messages(self):
        if os.path.isfile(self.path):
            return 1
        count = 0
        for file in chain.from_iterable((files for _, _, files in os.walk(self.path))):
            if '.eml' in file: count += 1
        return count

    def messages(self):
        companion_files = []
        if os.path.isfile(self.path):
            fileList = [self.path]
        else:
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
                        derivativesPath = common.normalizePath(unsafePath)
                    except Exception as e:
                        desc = "Error reading message path from headers"
                        errors = common.handle_error(errors, e, desc)

                    decoded_Message_ID, errors = format.parse_header(msg["message-id"], errors)
                    decoded_Date, errors = format.parse_header(msg["date"], errors)
                    decoded_From, errors = format.parse_header(msg["from"], errors)
                    decoded_To, errors = format.parse_header(msg["to"], errors)
                    decoded_Cc, errors = format.parse_header(msg["cc"], errors)
                    decoded_Bcc, errors = format.parse_header(msg["bcc"], errors)
                    decoded_Subject, errors = format.parse_header(msg["subject"], errors)

                    message = Email(
                        Errors=errors,
                        Message_ID=decoded_Message_ID,
                        Original_File=originalFile,
                        Message_Path=messagePath,
                        Derivatives_Path=derivativesPath,
                        Date=decoded_Date,
                        From=decoded_From,
                        To=decoded_To,
                        Cc=decoded_Cc,
                        Bcc=decoded_Bcc,
                        Subject=decoded_Subject,
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
            new_path, new_errors = format.moveWithDirectoryStructure(
                self.dry_run, self.keep, self.source_parent_dir, self.mailbag_dir, self.mailbag_name, self.format_name, filePath, errors
            )
            errors.extend(new_errors)
            message.Errors.extend(errors)

            yield message

        if self.companion_files:
            # Move all files into mailbag directory structure
            log.debug("Moving compantion files...")
            for companion_file in companion_files:
                new_path = format.moveWithDirectoryStructure(
                    self.dry_run,
                    self.keep,
                    self.source_parent_dir,
                    self.mailbag_dir,
                    self.mailbag_name,
                    self.format_name,
                    companion_file,
                    [],
                )
