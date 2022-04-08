import datetime
import json
from os.path import join
import mailbag.helper as helper
import mailbox
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email, Attachment
import email
import glob, os
from email import policy

log = get_logger()


class EML(EmailAccount):
    """EML - This concrete class parses eml file format"""
    format_name = 'eml'

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

        files = glob.glob(os.path.join(self.file, "**", "*.eml"), recursive=True)

        for filePath in files:

            subFolder = helper.emailFolder(self.file, filePath)

            error = []
            attachments = []
            
            try:
                with open(filePath, 'rb') as f:
                    msg = email.message_from_binary_file(f, policy=policy.default)

                    try:
                        html_body = None
                        html_bytes = None
                        text_body = None
                        text_bytes = None
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = part.get_content_disposition()
                                # character_set = part.get_charsets()
                                if content_type == "text/html" and content_disposition != "attachment":
                                    html_bytes = part.get_payload(decode=True)
                                    html_body = part.get_payload()
                                if content_type == "text/plain" and content_disposition != "attachment":
                                    text_bytes = part.get_payload(decode=True)
                                    text_body = part.get_payload()
                        else:
                            content_type = msg.get_content_type()
                            content_disposition = msg.get_content_disposition()
                            if content_type == "text/html" and content_disposition != "attachment":
                                html_bytes = part.get_payload(decode=True)
                                html_body = part.get_payload()
                            if content_type == "text/plain" and content_disposition != "attachment":
                                text_bytes = part.get_payload(decode=True)
                                text_body = part.get_payload()
                    except Exception as e:
                        log.error(e)
                        error.append("Error parsing message body.")

                    try:
                        # Extract Attachments                
                        for msgAttachment in msg.iter_attachments():
                            attachmentName, attachmentFile = helper.saveAttachments(msgAttachment)
                            attachment = Attachment(
                                                    Name=attachmentName if attachmentName else str(len(attachments)),
                                                    File=attachmentFile,
                                                    MimeType=msgAttachment.get_content_type()
                                                    )
                            attachments.append(attachment)
                            
                    except Exception as e:
                        log.error(e)
                        error.append("Error parsing attachments.")
                                        
                    message = Email(
                            Error=error,
                            Message_ID=msg["message-id"].strip(),
                            Message_Path=subFolder,
                            Original_Filename=str(os.path.basename(filePath)),
                            Date=msg["date"],
                            From=msg["from"],
                            To=msg["to"],
                            Subject=msg["subject"],
                            Content_Type=msg.get_content_type(),
                            Headers=msg,
                            HTML_Bytes=html_bytes,
                            HTML_Body=html_body,
                            Text_Bytes=text_bytes,
                            Text_Body=text_body,
                            Message=msg,
                            Attachments=attachments
                        )

            except (email.errors.MessageParseError, Exception) as e:
                message = Email(
                    Error=error.append('Error parsing message.')
                )

            # Move EML to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,self.file,self.mailbag_name,self.format_name,subFolder,filePath)
            yield message
