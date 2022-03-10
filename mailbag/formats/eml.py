import datetime
import json
from os.path import join
import mailbag.helper as helper
import mailbox
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email
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
        # self.dry_run = dry_run
        # self.mailbag_name = mailbag_name
        log.info("Reading : ", File=self.file)

    def account_data(self):
        return account_data

    def messages(self):

        files = glob.glob(os.path.join(self.file, "**", "*.eml"), recursive=True)

        for i in files:
            attachmentNames = []
            attachments = []
            with open(i, 'r') as f:
                msg = email.message_from_file(f, policy=policy.default)
                body = msg.get_body(preferencelist=('related', 'html', 'plain')).__str__()

                # Extract Attachments                
                for attachment in msg.iter_attachments():
                    attachmentName, attachment = helper.saveAttachments(attachment)
                    if attachmentName:
                        attachmentNames.append(attachmentName)
                    else:
                        attachmentNames.append(str(len(attachmentNames)))
                    attachments.append(attachment)
                
                if msg.is_multipart():
                        
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            html_body = part.get_payload()
                        elif part.get_content_type() == "text/plain":
                            text_body = part.get_payload()
                            log.debug("Content-type "+part.get_content_maintype())
                                
            message = Email(
                    # Email_Folder=helper.emailFolder(self.dry_run, self.mailbag_name, self.format_name, self.file,i),
                    Message_ID=msg["Message-id"],
                    Date=msg["date"],
                    From=msg["from"],
                    To=msg["to"],
                    Subject=msg["subject"],
                    Content_Type=msg["content-type"],
                    Body=body,
                    AttachmentNum=len(attachmentNames) if attachmentNames else 0,
                    AttachmentNames=attachmentNames,
                    AttachmentFiles=attachments,
                    Error='False'
                )

            yield message
