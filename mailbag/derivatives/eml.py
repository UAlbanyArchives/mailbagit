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

    def do_task_per_message(self, message, args):
        a = message.Message
        print("Message",args.directory)
        print(args.mailbag_name)



        msg = MIMEMultipart('alternative')

        msg['Subject'] = message.Subject
        msg['From'] = message.From
        msg['To'] = message.To
        msg['Cc'] = message.Cc
        msg['Bcc'] = message.Bcc


        if(message.Message is not None):
            msg.attach(message.Message)
        elif (message.Headers is not None):
           part=MIMEText(message.Text_Body)
           msg.attach(part)
           msg.attach(message.Headers)



        new_path = os.path.join(args.directory, args.mailbag_name, "data")

        log.debug("Writing EML to " + str(new_path))

        name=str(message.Mailbag_Message_ID)+".eml"
        outfile_name = os.path.join(new_path, name)
        with open(outfile_name, 'w') as outfile:
                gen = generator.Generator(outfile)
                gen.flatten(msg)





