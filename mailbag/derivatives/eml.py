# This is an example derivative, meant to show how
# to hook up a real parser

# Does nothing currently
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

log = get_logger()
class ExampleDerivative(Derivative):
    derivative_name = 'eml'

    def __init__(self,email_account, **kwargs):
        print("Setup account")
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
        new_path = os.path.join(out_dir, "data")

        log.debug("Writing EML to " + str(new_path))
        if self.args.dry_run:
            outfile_name = os.path.join(new_path,"derivative.eml")
            with open(outfile_name,'w') as outfile:
                gen = generator.Generator(outfile)
                gen.flatten(msg)


