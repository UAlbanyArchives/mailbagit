# This is an example derivative, meant to show how
# to hook up a real parser

# Does nothing currently
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import generator
from mailbag.derivative import Derivative
class ExampleDerivative(Derivative):
    derivative_name = 'eml'

    def __init__(self, email_account, **kwargs):
        print("Setup account")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message):
        html=message.HTML_Body
        part = MIMEText(html,'html')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = message.Subject
        msg['From'] = message.From
        msg['To'] = message.To
        msg['Cc'] = message.Cc
        msg['Bcc'] = message.Bcc
        msg.attach(part)


        outfile_name = os.path.join("/data", "email_samplenew.eml")
        with open(outfile_name, 'w') as outfile:
            gen = generator.Generator(outfile)
            gen.flatten(msg)





