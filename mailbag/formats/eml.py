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
import extract_msg


log = get_logger()


class EML(EmailAccount):
    """EML - This concrete class parses eml file format"""
    format_name = 'eml'

    def __init__(self, target_account,args, **kwargs):
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


            try:
                with open(filePath, 'r') as f:
                    msg = email.message_from_file(f)
                    
                    # Try to parse content
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                html_body = part.get_payload()
                            elif part.get_content_type() == "text/plain":
                                text_body = part.get_payload()

                    message = Email(
                            Email_Folder=subFolder,
                            Message_ID=msg["Message-id"],
                            Date=msg["date"],
                            From=msg["from"],
                            To=msg["to"],
                            Subject=msg["subject"],
                            Content_Type=msg["content-type"],
                            Headers = msg,
                            Text_Body = text_body,
                            HTML_Body = html_body,
                            Message = msg,
                            Error = 'False'
                                )
                    
                    # Make sure the EML file is closed
                    f.close()
                    
            except (email.errors.MessageParseError, Exception) as e:
                log.error(e)
                message = Email(
                    Error='True'
                )
            
            # Move EML to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run, self.file, self.mailbag_name,
                                                         self.format_name, subFolder, filePath)
            yield message
