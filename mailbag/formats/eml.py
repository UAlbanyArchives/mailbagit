import datetime
import json
import traceback
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
        self.dry_run = args.dry_run
        self.mailbag_name = args.mailbag_name
        log.info("Reading : ", File=self.file)

    def account_data(self):
        return account_data

    def messages(self):

        files = glob.glob(os.path.join(self.file, "**", "*.eml"), recursive=True)

        for filePath in files:

            originalFile = helper.relativePath(self.file, filePath)

            error = []
            stack_trace=[]
            try:
                with open(filePath, 'rb') as f:
                    msg = email.message_from_binary_file(f, policy=policy.default)

                    try:
                        # Parse message bodies
                        html_body = None
                        text_body = None
                        html_encoding = None
                        text_encoding = None
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = part.get_content_disposition()
                                if content_type == "text/html" and content_disposition != "attachment":
                                    html_encoding = part.get_charsets()[0]
                                    html_body = part.get_payload(decode=True).decode(html_encoding)
                                if content_type == "text/plain" and content_disposition != "attachment":
                                    text_encoding = part.get_charsets()[0]
                                    text_body = part.get_payload(decode=True).decode(text_encoding)
                        else:
                            content_type = msg.get_content_type()
                            content_disposition = msg.get_content_disposition()
                            if content_type == "text/html" and content_disposition != "attachment":
                                html_encoding = part.get_charsets()[0]
                                html_body = part.get_payload(decode=True).decode(html_encoding)
                            if content_type == "text/plain" and content_disposition != "attachment":
                                text_encoding = part.get_charsets()[0]
                                text_body = part.get_payload(decode=True).decode(text_encoding)
                    except Exception as e:
                        desc = "Error parsing message body"
                        error_msg = desc + ": " + repr(e)
                        error.append(error_msg)
                        stack_trace.append(traceback.format_exc())
                        log.error(error_msg)


                    # Look for message arrangement
                    try:
                        messagePath = helper.messagePath(msg)
                        unsafePath = os.path.join(os.path.dirname(originalFile), messagePath)
                        derivativesPath = helper.normalizePath(unsafePath)
                    except Exception as e:
                        log.error(e)
                        error.append("Error reading message path from headers.")


                    try:
                        # Extract Attachments
                        attachmentNames = []
                        attachments = []                
                        for attachment in msg.iter_attachments():
                            attachmentName, attachment = helper.saveAttachments(attachment)
                            if attachmentName:
                                attachmentNames.append(attachmentName)
                            else:
                                attachmentNames.append(str(len(attachmentNames)))
                            attachments.append(attachment)
                    except Exception as e:
                        desc = "Error parsing attachments"
                        error_msg = desc + ": " + repr(e)
                        error.append(error_msg)
                        stack_trace.append(traceback.format_exc())
                        log.error(error_msg)

                                    
                    message = Email(
                            Error=error,
                            Message_ID=msg["message-id"].strip(),
                            Original_File=originalFile,
                            Message_Path=messagePath,
                            Derivatives_Path=derivativesPath,
                            Date=msg["date"],
                            From=msg["from"],
                            To=msg["to"],
                            Subject=msg["subject"],
                            Content_Type=msg.get_content_type(),
                            Headers=msg,
                            HTML_Body=html_body,
                            HTML_Encoding=html_encoding,
                            Text_Body=text_body,
                            Text_Encoding=text_encoding,
                            Message=msg,
                            AttachmentNum=len(attachmentNames) if attachmentNames else 0,
                            AttachmentNames=attachmentNames,
                            AttachmentFiles=attachments,
                            StackTrace=stack_trace
                        )

            except (email.errors.MessageParseError, Exception) as e:
                desc = 'Error parsing message'
                error_msg = desc + ": " + repr(e)
                message = Email(
                    Error=error.append(error_msg),
                    StackTrace=stack_trace.append(traceback.format_exc())
                )
                log.error(error_msg)


            # Move EML to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,self.file,self.mailbag_name,self.format_name,filePath)
            yield message
