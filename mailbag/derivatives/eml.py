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
        new_path = os.path.join(args.directory, args.mailbag_name, "eml")
        name = str(message.Mailbag_Message_ID)+".eml"
        outfile_name = os.path.join(new_path, name)
        log.debug("Writing EML to " + str(outfile_name))
        #Generating eml file
        if not args.dry_run:
            if not os.path.isdir(new_path):
                os.mkdir(new_path)
            if message.Message is not None:
                with open(outfile_name, 'w') as outfile:
                    gen = generator.Generator(outfile)
                    gen.flatten(message.Message)
            elif message.Headers is not None:
                with open(outfile_name, 'w') as outfile:
                    gen = generator.Generator(outfile)
                    msg = MIMEMultipart('alternative')
                    for key in message.Headers:
                        value = message.Headers[key]
                        msg[key] = value

                    msg.attach(MIMEText(message.Text_Body))
                    msg.attach(MIMEText(message.HTML_Body, 'html'))
                    gen.flatten(msg)
            else:
                log.error("Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID))











