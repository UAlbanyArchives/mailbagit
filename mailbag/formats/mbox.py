import email
import mailbox

from structlog import get_logger
from pathlib import Path
import os, shutil, glob
import email.errors

from mailbag.email_account import EmailAccount
from mailbag.models import Email, Attachment
import mailbag.helper as helper
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

        self.file = target_account
        self.dry_run = args.dry_run
        self.mailbag_name = args.mailbag_name
        log.info("Reading : ", File=self.file)

    def account_data(self):
        return account_data

    def messages(self):

        if os.path.isfile(self.file):
            files = self.file
            parent_dir = os.path.dirname(self.file)
        else:
            files = os.path.join(self.file, "**", "*.mbox")
            parent_dir = self.file
        file_list = glob.glob(files, recursive=True)
        for filePath in file_list:
            originalFile = helper.relativePath(self.file, filePath)

            data = mailbox.mbox(filePath)
            for mail in data.itervalues():

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
                                bodies, attachments, errors = helper.parse_part(
                                    part, bodies, attachments, errors
                                )
                        else:
                            bodies, attachments, errors = helper.parse_part(
                                part, bodies, attachments, errors
                            )
                    except Exception as e:
                        desc = "Error parsing message parts"
                        errors = helper.handle_error(errors, e, desc)

                    # Look for message arrangement
                    try:
                        messagePath = helper.messagePath(mailObject)
                        if len(messagePath) > 0:
                            unsafePath = os.path.join(os.path.splitext(originalFile)[0], messagePath)
                        else:
                            unsafePath = os.path.splitext(originalFile)[0]
                        derivativesPath = helper.normalizePath(unsafePath)
                    except Exception as e:
                        desc = "Error reading message path from headers"
                        errors = helper.handle_error(errors, e, desc)

                    message = Email(
                        Error=errors["msg"],
                        Message_ID=mail["Message-ID"].strip(),
                        Original_File=originalFile,
                        Message_Path=messagePath,
                        Derivatives_Path=derivativesPath,
                        Date=mail["Date"],
                        From=mail["From"],
                        To=mail["To"],
                        Cc=mail["Cc"],
                        Bcc=mail["Bcc"],
                        Subject=mail["Subject"],
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
                    errors = helper.handle_error(errors, e, desc)
                    message = Email(Error=errors["msg"], StackTrace=errors["stack_trace"])
                    log.error(error_msg)

                yield message

            # Make sure the MBOX file is closed
            data.close()
            # Move MBOX to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run, parent_dir, self.mailbag_name, self.format_name, filePath)
