import extract_msg
import os
from pathlib import Path
from email import parser
from structlog import get_logger
import email.errors
from mailbagit.email_account import EmailAccount
from mailbagit.models import Email, Attachment
import mailbagit.helper.format as format
import mailbagit.helper.common as common
import mailbagit.globals as globals
from extract_msg import attachment
import uuid

log = get_logger()


class MSG(EmailAccount):
    """MSG - This concrete class parses msg file format"""

    format_name = "msg"
    format_agent = extract_msg.__name__
    format_agent_version = extract_msg.__version__

    def __init__(self, target_account, args, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.path = target_account
        self.dry_run = args.dry_run
        self.mailbag_name = args.mailbag_name
        self.companion_files = args.companion_files
        self.iteration_only = False
        log.info("Reading :", Path=self.path)

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
            # Parse email matching the input file extension

            if self.iteration_only:
                yield None
                continue

            originalFile = Path(format.relativePath(self.path, filePath)).as_posix()

            attachments = []
            errors = []
            try:
                mail = extract_msg.openMsg(filePath)
                # Parse message bodies
                html_body = None
                text_body = None
                html_encoding = None
                text_encoding = None
                try:
                    if mail.htmlBody:
                        html_body = mail.htmlBody.decode("utf-8").strip()
                        html_encoding = "utf-8"
                    if mail.body:
                        text_body = mail.body
                        text_encoding = mail.stringEncoding
                except Exception as e:
                    desc = "Error parsing message body"
                    errors = common.handle_error(errors, e, desc)

                # Look for message arrangement
                try:
                    messagePath = Path(format.messagePath(mail.header)).as_posix()
                    if messagePath == ".":
                        messagePath = ""
                    unsafePath = os.path.join(os.path.dirname(originalFile), messagePath)
                    derivativesPath = Path(format.normalizePath(unsafePath)).as_posix()
                except Exception as e:
                    desc = "Error reading message path from headers"
                    errors = common.handle_error(errors, e, desc)

                try:
                    for mailAttachment in mail.attachments:
                        if mailAttachment.getFilename():
                            attachmentName = mailAttachment.getFilename()
                        elif mailAttachment.longFilename:
                            attachmentName = mailAttachment.longFilename
                        elif mailAttachment.shortFilename:
                            attachmentName = mailAttachment.shortFilename
                        else:
                            attachmentName = None
                            desc = "No filename found for attachment, integer will be used instead"
                            errors = common.handle_error(errors, None, desc)

                        # Handle attachments.csv conflict
                        # helper.controller.writeAttachmentsToDisk() handles this
                        if attachmentName:
                            if attachmentName.lower() == "attachments.csv":
                                desc = "attachment " + attachmentName + " will be renamed to avoid filename conflict with mailbag spec"
                                errors = common.handle_error(errors, None, desc, "warn")

                        # Try to get the mime, guess it if this doesn't work
                        mime = None
                        try:
                            mime = mailAttachment.mimetype
                        except Exception as e:
                            desc = "Error reading mime type, guessing it instead"
                            errors = common.handle_error(errors, e, desc, "warn")
                        if mime is None:
                            mime = format.guessMimeType(attachmentName)

                        contentID = None
                        try:
                            contentID = mailAttachment.contendId
                        except Exception as e:
                            desc = "Error reading ContentID, creating an ID instead"
                            errors = common.handle_error(errors, e, desc, "warn")
                        if contentID is None:
                            contentID = uuid.uuid4().hex

                        attachment = Attachment(
                            Name=attachmentName,
                            File=mailAttachment.data,
                            MimeType=mime,
                            Content_ID=contentID,
                        )
                        attachments.append(attachment)

                except Exception as e:
                    desc = "Error parsing attachments"
                    errors = common.handle_error(errors, e, desc)

                message = Email(
                    Errors=errors,
                    Message_ID=mail.messageId.strip(),
                    Original_File=originalFile,
                    Message_Path=messagePath,
                    Derivatives_Path=derivativesPath,
                    Date=mail.date,
                    From=mail.sender,
                    To=mail.to,
                    Cc=mail.cc,
                    Bcc=mail.bcc,
                    Subject=mail.subject,
                    Content_Type=mail.header.get_content_type(),
                    # mail.header appears to be a headers object oddly enough
                    Headers=mail.header,
                    HTML_Body=html_body,
                    HTML_Encoding=html_encoding,
                    Text_Body=text_body,
                    Text_Encoding=text_encoding,
                    # Doesn't look like we can feasibly get a full email.message.Message object for .msg
                    Message=None,
                    Attachments=attachments,
                )
                # Make sure the MSG file is closed
                mail.close()

            except (email.errors.MessageParseError, Exception) as e:
                desc = "Error parsing message"
                errors = common.handle_error(errors, e, desc)
                message = Email(Errors=errors)
                # Make sure the MSG file is closed
                mail.close()

            # Move MSG to new mailbag directory structure
            new_path = format.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, filePath)
            yield message

        if self.companion_files:
            # Move all files into mailbag directory structure
            for companion_file in companion_files:
                new_path = format.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, companion_file)
