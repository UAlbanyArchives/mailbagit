import extract_msg
import glob, os
from email import parser
from structlog import get_logger
from RTFDE.deencapsulate import DeEncapsulator
import email.errors

from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbag.helper as helper
from extract_msg import attachment

log = get_logger()


class MSG(EmailAccount):
    """MSG - This concrete class parses msg file format"""
    format_name = 'msg'

    def __init__(self, target_account, args, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.file = target_account
        self.dry_run = args.dry_run
        self.mailbag_name = args.mailbag_name
        log.info("Reading :", File=self.file)

    def account_data(self):
        return account_data

    def messages(self):
        files = glob.glob(os.path.join(self.file, "**", "*.msg"), recursive=True)
        for filePath in files:
            
            subFolder = helper.emailFolder(self.file, filePath)
            
            try:
                mail = extract_msg.openMsg(filePath)
                
                html_body = None
                error = False
                
                # Extract HTML from RTF if no HTML body
                try:
                    if mail.htmlBody:
                        html_body = mail.htmlBody
                    else:
                        rtf_obj = DeEncapsulator(mail.rtfBody)
                        rtf_obj.deencapsulate()
                        if rtf_obj.content_type == 'html':
                            html_body = rtf_obj.html
                except Exception as e:
                    log.error(e)
                    error = True

                attachmentNames = []
                attachments = []
                                
                for attachment in mail.attachments:
                    if attachment.longFilename:
                        attachmentNames.append(attachment.longFilename)
                    elif attachment.shortFilename:
                        attachmentNames.append(attachment.shortFilename)
                    else:
                        attachmentNames.append(str(len(attachmentNames)))
                    attachments.append(attachment.data)
                
                message = Email(
                    Email_Folder=subFolder,
                    Date=mail.date,
                    From=mail.sender,
                    To=mail.to,
                    Cc=mail.cc,
                    Bcc=mail.bcc ,
                    Subject=mail.subject,
                    # mail.header appears to be a headers object oddly enough
                    Headers=mail.header,
                    Body=html_body,
                    Text_Body=mail.body,
                    HTML_Body=html_body,
                    # Doesn't look like we can feasibly get a full email.message.Message object for .msg
                    Message=None,
                    AttachmentNum=len(attachmentNames),
                    AttachmentNames=attachmentNames,
                    AttachmentFiles=attachments,
                    Error= str(error)
                )
                # Make sure the MSG file is closed
                mail.close()
            
            except (email.errors.MessageParseError, Exception) as e:
                message = Email(
                    Error='True'
                )
 
            # Move MBOX to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,self.file,self.mailbag_name,self.format_name,subFolder,filePath)
            yield message
