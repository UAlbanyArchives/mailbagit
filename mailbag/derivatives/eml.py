#This is Eml derivative
from os.path import join
import mailbag.helper as helper
import os,glob
import mailbox
from mailbag.email_account import EmailAccount
from structlog import get_logger
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email import generator
from mailbag.derivative import Derivative


log = get_logger()
class EmlDerivative(Derivative):
    derivative_name = 'eml'
    derivative_format = 'eml'

    def __init__(self,email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.eml_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.eml_dir)

    def do_task_per_account(self):
        print(self.account.account_data())


    def do_task_per_message(self, message):

        out_dir = os.path.join(self.eml_dir, message.Derivatives_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))

        # Build msg
        if not message.Message and not message.Headers:
            log.error("Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID))
        else:
            if message.Message:
                msg = message.Message
            elif message.Headers:
                msg = MIMEMultipart('alternative')
                for key in message.Headers:
                    value = message.Headers[key]
                    msg[key] = value

                # Does not yet try to use HTML_Bytes or Text_Bytes
                body = False
                if message.HTML_Body:
                    body = True
                    msg.attach(MIMEText(message.HTML_Body, 'html', message.HTML_Encoding))
                if message.Text_Body:
                    body = True
                    msg.attach(MIMEText(message.Text_Body, 'plain', message.Text_Encoding))
                if body == False:
                    log.warn("No body present for " + str(message.Mailbag_Message_ID) + ". Created EML without message body.")

                # Attachments
                for attachment in message.Attachments:
                    mimeType = attachment.MimeType
                    if mimeType is None:
                        mimeType = "text/plain"
                        log.error("Mime type not found for the attachment. Set as "+mimeType+".")
                    mimeType = mimeType.split('/')
                    part = MIMEBase(mimeType[0], mimeType[1])
                    part.set_payload(attachment.File)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=attachment.Name)
                    msg.attach(part)
            else:
                log.error("Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID))

            # Write EML to disk
            log.debug("Writing EML to " + str(out_dir))
            if not self.args.dry_run:
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)
                with open(filename + ".eml",'w') as outfile:
                    gen = generator.Generator(outfile)
                    gen.flatten(msg)
                    outfile.close()
