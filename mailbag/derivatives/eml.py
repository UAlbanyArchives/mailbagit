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
from mailbag.controller import Controller

log = get_logger()
class ExampleDerivative(Derivative):
    derivative_name = 'eml'

    def __init__(self,email_account, **kwargs):
        print("Setup account")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message, args):
        new_path = os.path.join(args.directory, args.mailbag_name)
        log.debug("Writing EML to " + str(new_path))
        name = str(message.Mailbag_Message_ID)+".eml"
        outfile_name = os.path.join(new_path, name)
        #Generating eml file
        with open(outfile_name, 'w') as outfile:
            gen = generator.Generator(outfile)
            if message.Message is not None:
                gen.flatten(message.Message)
            else:
                msg = MIMEMultipart('alternative')
                for key in message.Headers:
                    value = message.Headers[key]
                    msg[key] = value

                msg.attach(MIMEText(message.Text_Body))
                msg.attach(MIMEText(message.HTML_Body, 'html'))
                gen.flatten(msg)











