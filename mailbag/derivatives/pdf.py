import os
import subprocess
import distutils.spawn
from mailbag.derivative import Derivative
from structlog import get_logger

log = get_logger()
class ExampleDerivative(Derivative):
    derivative_name = 'pdf'
    wkhtmltopdf = 'wkhtmltopdf.exe'
    
    def __init__(self, email_account, **kwargs):
        print("Setup account")
        if not distutils.spawn.find_executable(self.wkhtmltopdf):
            raise OSError("wkhtmltopdf.exe not found. To create PDF derivatives, ensure that wkhtmltopdf is installed and in PATH.")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message, args, mailbag_dir):
        
        
        #check to see which body to use
        body = False
        if message.HTML_Body:
            body = message.HTML_Body
        elif message.Text_Body:
            body = message.Text_Body
        else:
            log.debug("Unable to create PDF, no body found for " + str(message.Mailbag_Message_ID))

        if body:
            table="<table>"
            headerFields=[]
            #Getting all the required attributes of message except error and body
            for attribute in message:
                if(attribute[0] not in ("Error","Text_Body","HTML_Body","Message","Headers") ):
                    headerFields.append(attribute[0])
            #Getting the values of the attrbutes and appending to HTML string
            for headerField in headerFields:
                if not getattr(message,headerField) is None:
                    table += "<tr>"
                    table += "<td>"+str(headerField)+"</td>"
                    table += "<td>"+str(getattr(message,headerField))+"</td>"
                    table += "</tr>"
            table += "</table>"

            #add headers table to html
            if message.HTML_Body and "<body" in body.lower():
                body_position = body.lower().index("<body")
                table_position = body_position + body[body_position:].index(">") + 1
                html_content = body[:table_position] + table + body[table_position:]
            else:
                #fallback to just prepending the table
                html_content = table + body

            if message.Message_Path is None:
                pdf_path = os.path.join(mailbag_dir, self.derivative_format)
            else:
                pdf_path = os.path.join(mailbag_dir, self.derivative_format, message.Message_Path)
            html_name = os.path.join(pdf_path, str(message.Mailbag_Message_ID )+".html")
            pdf_name = os.path.join(pdf_path, str(message.Mailbag_Message_ID )+".pdf")
            log.debug("Writing HTML to " + str(html_name) + " and converting to " + str(pdf_name))
            if not args.dry_run:
                if not os.path.isdir(pdf_path):
                        os.mkdir(pdf_path)
                write_html = open(html_name, 'w')
                write_html.write(html_content)
                write_html.close()
                p = subprocess.Popen([self.wkhtmltopdf, html_name, pdf_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if p.returncode == 0:
                    log.debug("Successfully created " + str(message.Mailbag_Message_ID )+".pdf")
                else:
                    if stdout:
                        log.error("Error creating " + str(message.Mailbag_Message_ID )+".pdf: " + str(stdout))
                    if stderr:
                        log.error("Error creating " + str(message.Mailbag_Message_ID )+".pdf: " + str(stderr))
                    #comment out for now since catches even very minor issues
                    #raise TypeError(stderr)
                # delete the HTML file
                os.remove(html_name)









