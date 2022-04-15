import os
import subprocess
import distutils.spawn
from mailbag.derivative import Derivative
from structlog import get_logger
import mailbag.helper as helper

# only create format if pypff is successfully importable -
# pst is not supported otherwise
skip_registry = False
try:
    if distutils.spawn.find_executable('wkhtmltopdf.exe'):
        wkhtmltopdf = 'wkhtmltopdf.exe'
    elif distutils.spawn.find_executable('wkhtmltopdf'):
        wkhtmltopdf = 'wkhtmltopdf'
    else:
        skip_registry = True
        wkhtmltopdf = None
except:
    skip_registry = True

log = get_logger()

if not skip_registry:

    class PDFDerivative(Derivative):
        derivative_name = 'pdf'
        derivative_format = 'pdf'
        
        def __init__(self, email_account, **kwargs):
            log.debug("Setup account")
            super()

            self.args = kwargs["args"]
            mailbag_dir = kwargs["mailbag_dir"]
            self.pdf_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
            if not self.args.dry_run:
                os.makedirs(self.pdf_dir)

        def do_task_per_account(self):
            print(self.account.account_data())

        def do_task_per_message(self, message):
            
            
            #check to see which body to use
            body = False
            if message.HTML_Body:
                body = message.HTML_Body
                encoding = message.HTML_Encoding
            elif message.Text_Body:
                body = message.Text_Body
                encoding = message.Text_Encoding
            else:
                log.debug("Unable to create PDF, no body found for " + str(message.Mailbag_Message_ID))

            if body:
                table="<table>"
                headerFields=[]
                #Getting all the required attributes of message except error and body
                for attribute in message:
                    if(attribute[0] not in ("Error","Text_Body", "Text_Bytes", "HTML_Body", "HTML_Bytes", "Message","Headers", "Attachments")):
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

                #add encoding
                meta = "<meta charset=\"" + encoding + "\">"
                if message.HTML_Encoding and "<head" in html_content.lower():
                    head_position = html_content.lower().index("<head")
                    meta_position = head_position + html_content[head_position:].index(">") + 1
                    html_encoded = html_content[:meta_position] + meta + html_content[meta_position:]
                else:
                    #fallback to just prepending the tag
                    html_encoded = meta + html_content

                out_dir = os.path.join(self.pdf_dir, message.Derivatives_Path)
                filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))
                html_name = filename + ".html"
                pdf_name = filename + ".pdf"

                log.debug("Writing HTML to " + str(html_name) + " and converting to " + str(pdf_name))
                if not self.args.dry_run:
                    if not os.path.isdir(out_dir):
                        os.makedirs(out_dir)
                    write_html = open(html_name, 'w', encoding=encoding)
                    write_html.write(html_encoded)
                    write_html.close()
                    p = subprocess.Popen([wkhtmltopdf, html_name, pdf_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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
