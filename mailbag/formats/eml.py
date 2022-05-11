import datetime
import json
from os.path import join
import mailbag.helper as helper
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email, Attachment
import email
import os
from email import policy
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
        self.iteration_only = False
        log.info("Reading : ", Path=self.path)

    def account_data(self):
        return account_data

    def messages(self):

        fileList = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.lower().endswith("." + self.format_name):
                    fileList.append(os.path.join(root, file))

        for filePath in fileList:

            if self.iteration_only:
                yield None
                continue

            originalFile = helper.relativePath(self.path, filePath)

            attachments = []
            errors = {}
            errors["msg"] = []
            errors["stack_trace"] = []
            try:
                with open(filePath, "rb") as f:
                    msg = email.message_from_binary_file(f, policy=policy.default)

                    try:
                        # Parse message bodies
                        bodies = {}
                        bodies["html_body"] = None
                        bodies["text_body"] = None
                        bodies["html_encoding"] = None
                        bodies["text_encoding"] = None
                        if msg.is_multipart():
                            for part in msg.walk():
                                bodies, attachments, errors = helper.parse_part(part, bodies, attachments, errors)
                        else:
                            bodies, attachments, errors = helper.parse_part(msg, bodies, attachments, errors)

                    except Exception as e:
                        desc = "Error parsing message parts"
                        errors = helper.handle_error(errors, e, desc)

                    # Look for message arrangement
                    try:
                        messagePath = helper.messagePath(msg)
                        unsafePath = os.path.join(os.path.dirname(originalFile), messagePath)
                        derivativesPath = helper.normalizePath(unsafePath)
                    except Exception as e:
                        desc = "Error reading message path from headers"
                        errors = helper.handle_error(errors, e, desc)

                    message = Email(
                        Error=errors["msg"],
                        Message_ID=helper.parse_header(msg["message-id"]),
                        Original_File=originalFile,
                        Message_Path=messagePath,
                        Derivatives_Path=derivativesPath,
                        Date=helper.parse_header(msg["date"]),
                        From=helper.parse_header(msg["from"]),
                        To=helper.parse_header(msg["to"]),
                        Subject=helper.parse_header(msg["subject"]),
                        Content_Type=msg.get_content_type(),
                        Headers=msg,
                        HTML_Body=bodies["html_body"],
                        HTML_Encoding=bodies["html_encoding"],
                        Text_Body=bodies["text_body"],
                        Text_Encoding=bodies["text_encoding"],
                        Message=msg,
                        Attachments=attachments,
                        StackTrace=errors["stack_trace"],
                    )

            except (email.errors.MessageParseError, Exception) as e:
                desc = "Error parsing message"
                errors = helper.handle_error(errors, e, desc)
                message = Email(Error=errors["msg"], StackTrace=errors["stack_trace"])

            # Move EML to new mailbag directory structure
            yield message
            new_path = helper.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, filePath)
