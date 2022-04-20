from structlog import get_logger
import mailbox
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

log = get_logger()

from mailbag.derivative import Derivative
class MboxDerivative(Derivative):
    derivative_name = 'mbox'
    derivative_format = 'mbox'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.mbox_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.mbox_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())


    def do_task_per_message(self, message):

        if len(message.Derivatives_Path) < 1:
            out_dir = self.mbox_dir
            filename = os.path.join(out_dir, self.args.mailbag_name + ".mbox")
        elif len(message.Derivatives_Path.strip(os.sep).split(os.sep)) == 1:
            out_dir = self.mbox_dir
            filename = os.path.join(out_dir, message.Derivatives_Path.strip(os.sep) + ".mbox")
        else:
            out_dir = os.path.join(self.mbox_dir, os.path.dirname(message.Derivatives_Path.strip(os.sep)))
            filename = os.path.join(out_dir, os.path.basename(message.Derivatives_Path.strip(os.sep)) + ".mbox")

        log.debug("Writing message to " + str(filename))
        if not self.args.dry_run:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)

            mbox = mailbox.mbox(filename)
            mbox.lock()
            if message.Message:
                mbox.add(message.Message)
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
                    log.warn("No body present for " + str(message.Mailbag_Message_ID) + ". Added message to MBOX without message body.")
                
                # Attachments
                for attachment in message.Attachments:
                    mimeType = "text/plain" if attachment.MimeType is None else attachment.MimeType
                    mimeType = mimeType.split('/')
                    part = MIMEBase(mimeType[0], mimeType[1])
                    part.set_payload(attachment.File)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=attachment.Name)
                    msg.attach(part)
                    
                mbox.add(msg)

            else:
                log.error("Unable to write message to MBOX as no body or headers present for " + str(message.Mailbag_Message_ID))

            mbox.flush()
            mbox.unlock()