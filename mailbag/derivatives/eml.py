#This is Eml derivative
from os.path import join
import mailbag.helper as helper
import os,glob
import mailbox
from mailbag.email_account import EmailAccount
from structlog import get_logger
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import generator
from mailbag.derivative import Derivative


log = get_logger()
class ExampleDerivative(Derivative):
    derivative_name = 'eml'
    derivative_format = 'eml'

    def __init__(self,email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())


    def do_task_per_message(self, message, args, mailbag_dir):

        if message.Message_Path is None:
            out_dir = os.path.join(mailbag_dir, self.derivative_format)
        else:
            out_dir = os.path.join(mailbag_dir, self.derivative_format, message.Message_Path)
        norm_dir=helper.normalizePath(out_dir)

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
                    msg.attach(MIMEText(message.HTML_Body, 'html'))
                if message.Text_Body:
                    body = True
                    msg.attach(MIMEText(message.Text_Body))
                if body == False:
                    log.warn("No body present for " + str(message.Mailbag_Message_ID) + ". Created EML without message body.")

                # Attachments
                #Missing
            else:
                log.error("Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID))

            # Write EML to disk
            log.debug("Writing EML to " + str(norm_dir))
            if not args.dry_run:
                outfile_name = os.path.join(out_dir,str(message.Mailbag_Message_ID) + "." + self.derivative_format)
                norm_filename = helper.normalizePath(outfile_name)
                if not os.path.isdir(norm_dir):
                    os.makedirs(norm_dir)
                with open(norm_filename,'w') as outfile:
                    gen = generator.Generator(outfile)
                    gen.flatten(msg)
