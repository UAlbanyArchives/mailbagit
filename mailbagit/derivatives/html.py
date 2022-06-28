# Makes html derivatives just containing message bodies
import os
import mailbagit.helper.derivative as derivative
import mailbagit.helper.common as common
from structlog import get_logger

log = get_logger()

from mailbagit.derivative import Derivative


class HtmlDerivative(Derivative):
    derivative_name = "html"
    derivative_format = "html"
    derivative_agent = ""
    derivative_agent_version = ""

    def __init__(self, email_account, args, mailbag_dir):
        log.debug("Setup account")

        # Sets up self.format_subdirectory
        super().__init__(args, mailbag_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        errors = []
        try:

            if message.Derivatives_Path is None:
                out_dir = self.format_subdirectory
            else:
                out_dir = os.path.join(self.format_subdirectory, message.Derivatives_Path)
            errors = common.check_path_length(out_dir, errors)
            filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".html")
            errors = common.check_path_length(filename, errors)

            if message.HTML_Body is None and message.Text_Body is None:
                desc = "No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ", no HTML derivative created"
                errors = common.handle_error(errors, None, desc, "warn")
            else:
                log.debug("Writing html derivative to " + filename)
                # Calling helper function to get formatted html
                html_formatted = None
                try:
                    html_formatted, encoding = derivative.htmlFormatting(message, self.args.css, headers=False)
                except Exception as e:
                    desc = "Error formatting HTML for HTML derivative"
                    errors = common.handle_error(errors, e, desc)

                if not self.args.dry_run:
                    if html_formatted:
                        try:
                            if not os.path.isdir(out_dir):
                                os.makedirs(out_dir)
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(html_formatted)
                                f.close()
                        except Exception as e:
                            desc = "Error writing HTML derivative"
                            errors = common.handle_error(errors, e, desc)

        except Exception as e:
            desc = "Error creating HTML derivative"
            errors = common.handle_error(errors, e, desc)

        message.Errors.extend(errors)

        return message
