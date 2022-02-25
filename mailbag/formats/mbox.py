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
        
        files = glob.glob(os.path.join(self.file, "**", "*.mbox"), recursive=True)
        for filePath in files:
            subFolder = helper.emailFolder(self.file, filePath)

            data = mailbox.mbox(filePath)
            for mail in data.itervalues():
                try:
                    mailObject = email.message_from_bytes(mail.as_bytes(), policy=email.policy.default)
                    print (dir(mail))
                    # Try to parse content
                    attachmentNames = []
                    attachments = []
                    
                    body = mailObject.get_body(preferencelist=('related', 'html', 'plain')).__str__()
                    
                    # Extract Attachments
                    for attached in mailObject.iter_attachments():
                        attachmentName, attachment = helper.saveAttachments(attached)
                        if attachmentName:
                            attachmentNames.append(attachmentName)
                            attachments.append(attachment)
                    if mail.is_multipart():
                        
                        for part in mail.walk():
                            if part.get_content_type() == "text/html":
                                html_body = part.get_payload()
                            elif part.get_content_type() == "text/plain":
                                text_body = part.get_payload()
                                log.debug("Content-type " + part.get_content_maintype())

                    message = Email(
                        Message_ID=mail['Message-ID'],
                        Email_Folder=subFolder,
                        Date=mail['Date'],
                        From=mail['From'],
                        To=mail['To'],
                        Cc=mail['Cc'],
                        Bcc=mail['Bcc'],
                        Subject=mail['Subject'],
                        Content_Type=mail['Content-Type'],
                        Headers=mail,
                        Body=body,
                        Text_Body=text_body,
                        HTML_Body=html_body,
                        Message=mailObject,
                        AttachmentNum=len(attachmentNames) if attachmentNames else 0,
                        AttachmentNames=attachmentNames,
                        AttachmentFiles=attachments,
                        Error='False'
                    )
                except (email.errors.MessageParseError, Exception) as e:
                    log.error(e)
                    message = Email(
                        Error='True'
                    )
                yield message

            # Make sure the MBOX file is closed
            data.close()
            # Move MBOX to new mailbag directory structure
            # new_path = helper.moveWithDirectoryStructure(self.dry_run, self.file, self.mailbag_name, self.format_name, subFolder, filePath)
