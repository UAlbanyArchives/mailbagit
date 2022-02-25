import os
import subprocess

from mailbag.derivative import Derivative


class ExampleDerivative(Derivative):
    derivative_name = 'pdf'

    def __init__(self, email_account, **kwargs):
        print("Setup account")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message, args):
        wkhtmltopdf = 'wkhtmltopdf.exe'
        html = message.HTML_Body
        html_name = os.path.join(args.directory, args.mailbag_name,str(message.Mailbag_Message_ID )+".html")
        pdf_name =os.path.join(args.directory, args.mailbag_name,str(message.Mailbag_Message_ID )+".pdf")
        write_html = open(html_name, 'w')
        write_html.write(html)
        write_html.close()
        s = subprocess.run([wkhtmltopdf,html_name,pdf_name])



