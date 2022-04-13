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

                html_formatted, encoding = helper.htmlFormatting(message, self.args.pdf_css)

                if html_formatted:

                    out_dir = os.path.join(self.pdf_dir, message.Derivatives_Path)
                    filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))
                    html_name = filename + ".html"
                    pdf_name = filename + ".pdf"

                    log.debug("Writing HTML to " + str(html_name) + " and converting to " + str(pdf_name))
                    if not self.args.dry_run:
                        if not os.path.isdir(out_dir):
                            os.makedirs(out_dir)
                        write_html = open(html_name, 'w', encoding=encoding)
                        write_html.write(html_formatted)
                        write_html.close()
                        p = subprocess.Popen([wkhtmltopdf, html_name, pdf_name], stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
                        stdout, stderr = p.communicate()
                        if p.returncode == 0:
                            log.debug("Successfully created " + str(message.Mailbag_Message_ID) + ".pdf")
                        else:
                            if stdout:
                                log.error("Error creating " + str(message.Mailbag_Message_ID) + ".pdf: " + str(stdout))
                            if stderr:
                                log.error("Error creating " + str(message.Mailbag_Message_ID) + ".pdf: " + str(stderr))
                            # comment out for now since catches even very minor issues
                            # raise TypeError(stderr)
                        # delete the HTML file
                        os.remove(html_name)


