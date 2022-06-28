import os
import subprocess
import distutils.spawn
from mailbagit.derivative import Derivative
from structlog import get_logger
import mailbagit.helper.derivative as derivative
import mailbagit.helper.common as common

# only create format if pypff is successfully importable -
# pst is not supported otherwise
skip_registry = False
try:
    if distutils.spawn.find_executable("wkhtmltopdf.exe"):
        wkhtmltopdf = "wkhtmltopdf.exe"
    elif distutils.spawn.find_executable("wkhtmltopdf"):
        wkhtmltopdf = "wkhtmltopdf"
    else:
        skip_registry = True
        wkhtmltopdf = None
except:
    skip_registry = True

log = get_logger()

if not skip_registry:

    class PDFDerivative(Derivative):
        derivative_name = "pdf"
        derivative_format = "pdf"
        derivative_agent = "wkhtmltopdf"
        check_version = subprocess.Popen([wkhtmltopdf, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = check_version.communicate()
        if len(err) > 0:
            log.error("Unable to access --version for " + derivative_agent + ": " + err.decode("utf-8"))
            raise Exception("Unable to access --version for " + derivative_agent + ": " + err.decode("utf-8"))
        derivative_agent_version = out.decode("utf-8").strip()

        def __init__(self, email_account, args, mailbag_dir):
            log.debug("Setup account")

            # Sets up self.format_subdirectory
            super().__init__(args, mailbag_dir)

        def do_task_per_account(self):
            print(self.account.account_data())

        def do_task_per_message(self, message):

            errors = []

            try:

                out_dir = os.path.join(self.format_subdirectory, message.Derivatives_Path)
                filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))
                errors = common.check_path_length(out_dir, errors)
                html_name = filename + ".html"
                pdf_name = filename + ".pdf"
                errors = common.check_path_length(pdf_name, errors)

                if message.HTML_Body is None and message.Text_Body is None:
                    desc = "No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ", no PDF derivative created"
                    errors = common.handle_error(errors, None, desc, "warn")
                else:
                    log.debug("Writing HTML to " + str(html_name) + " and converting to " + str(pdf_name))
                    # Calling helper function to get formatted html
                    try:
                        html_formatted, encoding = derivative.htmlFormatting(message, self.args.css)
                    except Exception as e:
                        desc = "Error formatting HTML for PDF derivative"
                        errors = common.handle_error(errors, e, desc)

                    if not self.args.dry_run:
                        try:
                            if not os.path.isdir(out_dir):
                                os.makedirs(out_dir)

                            with open(html_name, "w", encoding="utf-8") as write_html:
                                write_html.write(html_formatted)
                                write_html.close()
                            command = [
                                wkhtmltopdf,
                                "--disable-javascript",
                                os.path.abspath(html_name),
                                os.path.abspath(pdf_name),
                            ]
                            log.debug("Running " + " ".join(command))
                            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            stdout, stderr = p.communicate()
                            if p.returncode == 0:
                                log.debug("Successfully created " + str(message.Mailbag_Message_ID) + ".pdf")
                            else:
                                if stdout:
                                    log.debug("Output converting to " + str(message.Mailbag_Message_ID) + ".pdf: " + stdout.decode("utf-8"))
                                if stderr:
                                    desc = (
                                        "Error converting to "
                                        + str(message.Mailbag_Message_ID)
                                        + ".pdf: "
                                        + stderr.decode("utf-8").replace("\r", "\n").replace("\n\n", "\n")
                                    )
                                    errors = common.handle_error(errors, None, desc, "warn")
                            # delete the HTML file
                            if os.path.isfile(pdf_name):
                                os.remove(html_name)

                        except Exception as e:
                            desc = "Error writing HTML and converting to PDF derivative"
                            errors = common.handle_error(errors, e, desc)

            except Exception as e:
                desc = "Error creating PDF derivative"
                errors = common.handle_error(errors, e, desc)

            message.Errors.extend(errors)

            return message
