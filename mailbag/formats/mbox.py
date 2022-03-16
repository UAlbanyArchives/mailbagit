import email
import mailbox
from structlog import get_logger
from pathlib import Path
import os, shutil, glob
import email.errors

from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbag.helper as helper

log = get_logger()

class Mbox(EmailAccount):
    """Mbox - This concrete class parses mbox file format"""
    format_name = 'mbox'

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
            subFolder = helper.emailFolder(parent_dir, filePath, True)

            data = mailbox.mbox(filePath)
            for mail in data.itervalues():
                try:
                    error = []
                    mailObject = email.message_from_bytes(mail.as_bytes(),policy=email.policy.default)

                    # Try to parse content
                    try:
                        html_body = None
                        html_bytes = None
                        text_body = None
                        text_bytes = None
                        if mailObject.is_multipart():
                            for part in mailObject.walk():
                                content_type = part.get_content_type()
                                content_disposition = part.get_content_disposition()
                                #character_set = part.get_charsets()
                                if content_type == "text/html" and content_disposition != "attachment":
                                    html_bytes = part.get_payload(decode=True)
                                    html_body = part.get_payload()
                                if content_type == "text/plain" and content_disposition != "attachment":
                                    text_bytes = part.get_payload(decode=True)
                                    text_body = part.get_payload()
                        else:
                            content_type = mailObject.get_content_type()
                            content_disposition = mailObject.get_content_disposition()
                            if content_type == "text/html" and content_disposition != "attachment":
                                html_bytes = part.get_payload(decode=True)
                                html_body = part.get_payload()
                            if content_type == "text/plain" and content_disposition != "attachment":
                                text_bytes = part.get_payload(decode=True)
                                text_body = part.get_payload()
                    except Exception as e:
                        log.error(e)
                        error.append("Error parsing message body.")
                    
                    # Extract Attachments
                    attachmentNames = []
                    attachments = []
                    try:
                        for attached in mailObject.iter_attachments():
                            attachmentName,attachment = helper.saveAttachments(attached)
                            if attachmentName:
                                attachmentNames.append(attachmentName)
                                attachments.append(attachment)
                    except Exception as e:
                        log.error(e)
                        error.append("Error parsing attachments.")

                    message = Email(
                        Error=error,
                        Message_ID=mail['Message-ID'].strip(),
                        Message_Path=os.path.join(subFolder, os.path.splitext(os.path.basename(filePath))[0]),
                        Original_Filename=str(os.path.basename(filePath)),
                        Date=mail['Date'],
                        From=mail['From'],
                        To=mail['To'],
                        Cc=mail['Cc'],
                        Bcc=mail['Bcc'],
                        Subject=mail['Subject'],
                        Content_Type=mailObject.get_content_type(),
                        Headers=mail,
                        HTML_Bytes=html_bytes,
                        HTML_Body=html_body,
                        Text_Bytes=text_bytes,
                        Text_Body=text_body,
                        Message=mailObject,
                        AttachmentNum=len(attachmentNames) if attachmentNames else 0,
                        AttachmentNames=attachmentNames,
                        AttachmentFiles=attachments
                    )
                except (email.errors.MessageParseError, Exception) as e:
                    log.error(e)
                    message = Email(
                        Error=['Error parsing message.']
                    )
                yield message

            # Make sure the MBOX file is closed
            data.close()
            # Move MBOX to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,parent_dir,self.mailbag_name,self.format_name,subFolder,filePath)
