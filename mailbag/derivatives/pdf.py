import os
import subprocess
from mailbag.derivative import Derivative
from structlog import get_logger

log = get_logger()
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
        table="<table>"
        headerFields=[]
        #Getting all the required attributes of message except error and body
        for attribute in message:
            if(attribute[0] not in ("Error","Text_Body","HTML_Body","Message","Headers") ):
                headerFields.append(attribute[0])
        #Getting the values of the attrbutes and appending to HTML string
        for headerField in headerFields:
            if not getattr(message,headerField) is None:
                table= table+"<tr>"
                table= table+"<td>"+str(headerField)+"</td>"
                table= table+"<td>"+str(getattr(message,headerField))+"</td>"
                table= table+"</tr>"
        table=table+"</table>"
        table=table+html
        html_name = os.path.join(args.directory, args.mailbag_name,str(message.Mailbag_Message_ID )+".html")
        pdf_name = os.path.join(args.directory, args.mailbag_name,str(message.Mailbag_Message_ID )+".pdf")
        log.debug("Writing HTML to " + str(html_name))
        if not args.dry_run:
            write_html = open(html_name, 'w')
            write_html.write(table)
            write_html.close()
        p = subprocess.Popen([wkhtmltopdf, html_name, pdf_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr=p.communicate()
        if stdout:
            log.debug(stdout)
        if stderr:
            log.debug("Error while creating pdf")
            raise TypeError(stderr)








