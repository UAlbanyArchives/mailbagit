from structlog import get_logger
import mailbox
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = get_logger()

from mailbag.derivative import Derivative
class MboxDerivative(Derivative):
    derivative_name = 'mbox'
    derivative_format = 'mbox'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self):
        log.debug(self.account.account_data())


    def do_task_per_message(self, message, args, mailbag_dir):

        if message.Message_Path is None or message.Message_Path == ".":
            out_dir = os.path.join(mailbag_dir, self.derivative_format)
            # works for now, we probably need the new implementaion of Original-File and Derivatives-Path for this
            filename = args.mailbag_name
        else:
            out_dir = os.path.join(mailbag_dir, self.derivative_format, message.Message_Path)
            filename = os.path.basename(message.Message_Path)

        norm_dir = helper.normalizePath(out_dir)
        norm_filename = helper.normalizePath(filename)
        new_path = os.path.join(norm_dir,str(norm_filename) + ".mbox")
        log.debug("Writing message to " + str(new_path))
        if not args.dry_run:
            if not os.path.isdir(norm_dir):
                os.makedirs(norm_dir)

            mbox = mailbox.mbox(new_path)
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
                    msg.attach(MIMEText(message.HTML_Body, 'html'))
                if message.Text_Body:
                    body = True
                    msg.attach(MIMEText(message.Text_Body))
                if body == False:
                    log.warn("No body present for " + str(message.Mailbag_Message_ID) + ". Added message to MBOX without message body.")
                
                mbox.add(msg)
                # Attachments
                #Missing
            else:
                log.error("Unable to write message to MBOX as no body or headers present for " + str(message.Mailbag_Message_ID))

            mbox.flush()
            mbox.unlock()