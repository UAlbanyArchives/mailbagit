import extract_msg
import glob, os
from email import parser
from structlog import get_logger
from RTFDE.deencapsulate import DeEncapsulator
import email.errors
from mailbag.email_account import EmailAccount
from mailbag.models import Email, Attachment
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
            
            originalFile = helper.relativePath(self.file, filePath)
            
            attachments = []
            errors = {}
            errors["msg"] = []
            errors["stack_trace"] = []
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
                    errors = helper.handle_error(errors, e, desc)

                # Look for message arrangement
                try:
                    messagePath = helper.messagePath(mail.header)
                    unsafePath = os.path.join(os.path.dirname(originalFile), messagePath)
                    derivativesPath = helper.normalizePath(unsafePath)
                except Exception as e:
                    desc = "Error reading message path from headers"
                    errors = helper.handle_error(errors, e, desc)

                try:   
                    for mailAttachment in mail.attachments:
                        if mailAttachment.getFilename():
                            attachmentName = mailAttachment.getFilename()
                        elif mailAttachment.longFilename:
                            attachmentName = mailAttachment.longFilename
                        elif mailAttachment.shortFilename:
                            attachmentName = mailAttachment.shortFilename
                        else:
                            attachmentName = str(len(attachments))
                            desc = "No filename found for attachment " + attachmentName + \
                                " for message " + str(message.Mailbag_Message_ID)
                            errors = helper.handle_error(errors, e, desc)
                            
                        attachment = Attachment(
                                                Name=attachmentName,
                                                File=mailAttachment.data,
                                                MimeType=helper.guessMimeType(attachmentName)
                                                )
                        attachments.append(attachment)

                except Exception as e:
                    desc = "Error parsing attachments"
                    errors = helper.handle_error(errors, e, desc)


                message = Email(
                    Error = errors["msg"],
                    Message_ID = mail.messageId.strip(),
                    Original_File=originalFile,
                    Message_Path=messagePath,
                    Derivatives_Path=derivativesPath,
                    Date=mail.date,
                    From=mail.sender,
                    To=mail.to,
                    Cc=mail.cc,
                    Bcc=mail.bcc ,
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
                    StackTrace=errors["stack_trace"]
                )
                # Make sure the MSG file is closed
                mail.close()
            
            except (email.errors.MessageParseError, Exception) as e:
                desc = 'Error parsing message'
                errors = helper.handle_error(errors, e, desc)
                message = Email(
                    Error=errors["msg"],
                    StackTrace=errors["stack_trace"]
                    )
                # Make sure the MSG file is closed
                mail.close()
 
            # Move MSG to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run, self.file, self.mailbag_name, self.format_name, filePath)
            yield message
