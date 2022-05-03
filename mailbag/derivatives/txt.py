# Makes txt file derivatives just containing message bodies
import os
import mailbag.helper as helper
from structlog import get_logger

log = get_logger()

# Does nothing currently
from mailbag.derivative import Derivative


class TxtDerivative(Derivative):
    derivative_name = "txt"
    derivative_format = "txt"
    derivative_agent = ""
    derivative_agent_version = ""

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.txt_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.txt_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        errors = {}
        errors["msg"] = []
        errors["stack_trace"] = []

        try:

            out_dir = os.path.join(self.txt_dir, message.Derivatives_Path)
            filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".txt")

            if message.Text_Body is None:
                desc = "No plain text body for " + str(message.Mailbag_Message_ID) + ", no TXT derivative created"
                errors = helper.handle_error(errors, None, desc, "warn")
            else:
                log.debug("Writing txt derivative to " + filename)
                if not self.args.dry_run:
                    try:
                        if not os.path.isdir(out_dir):
                            os.makedirs(out_dir)
                        if message.Text_Body:
                            with open(filename, "w", encoding=message.Text_Encoding) as f:
                                f.write(message.Text_Body)
                                f.close()
                    except Exception as e:
                        desc = "Error writing plain text body to file"
                        errors = helper.handle_error(errors, e, desc)

        except Exception as e:
            desc = "Error creating plain text derivative"
            errors = helper.handle_error(errors, e, desc)

        message.Error.extend(errors["msg"])
        message.StackTrace.extend(errors["stack_trace"])

        return message
