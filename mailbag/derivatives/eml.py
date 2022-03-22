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
#from mailbag.controller import Controller

import mailbag.helper as helper


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

        html=message.HTML_Body
        part = MIMEText(html,'html')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = message.Subject
        msg['From'] = message.From
        msg['To'] = message.To
        msg['Cc'] = message.Cc
        msg['Bcc'] = message.Bcc
        msg.attach(part)
        norm_dir=helper.normalizePath(out_dir)

        log.debug("Writing EML to " + str(norm_dir))
        if not args.dry_run:
            outfile_name = os.path.join(out_dir,str(message.Mailbag_Message_ID) + "." + self.derivative_format)
            norm_filename = helper.normalizePath(outfile_name)
            if not os.path.isdir(norm_dir):
                os.makedirs(norm_dir)
            with open(norm_filename,'w') as outfile:
                gen = generator.Generator(outfile)
                gen.flatten(msg)



