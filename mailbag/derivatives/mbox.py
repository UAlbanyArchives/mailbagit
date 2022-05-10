from structlog import get_logger
import mailbox
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, charset
import platform

log = get_logger()

from mailbag.derivative import Derivative


class MboxDerivative(Derivative):
    derivative_name = "mbox"
    derivative_format = "mbox"
    derivative_agent = mailbox.__name__
    derivative_agent_version = platform.python_version()

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.mbox_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.mbox_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        errors = {}
        errors["msg"] = []
        errors["stack_trace"] = []

        try:

            try:
                if len(message.Derivatives_Path) < 1:
                    out_dir = self.mbox_dir
                    filename = os.path.join(out_dir, self.args.mailbag_name + ".mbox")
                elif len(message.Derivatives_Path.strip("/").split("/")) == 1:
                    out_dir = self.mbox_dir
                    filename = os.path.join(out_dir, message.Derivatives_Path.strip("/") + ".mbox")
                else:
                    out_dir = os.path.join(self.mbox_dir, os.path.dirname(message.Derivatives_Path.strip("/")))
                    filename = os.path.join(out_dir, os.path.basename(message.Derivatives_Path.strip(os.sep)) + ".mbox")
            except Exception as e:
                desc = "Error setting up MBOX derivative"
                errors = helper.handle_error(errors, e, desc)

            log.debug("Writing message to " + str(filename))
            if self.args.dry_run:
                # Checks for bodies to raise warnings even during a dry run
                if not message.HTML_Body and not message.Text_Body:
                    desc = "No body present for " + str(message.Mailbag_Message_ID) + ". Added message to MBOX without message body"
                    errors = helper.handle_error(errors, None, desc, "warn")
            else:
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)

                try:

                    mbox = mailbox.mbox(filename)
                    mbox.lock()

                    fullObjectWrite = False
                    if message.Message:
                        mbox.add(message.Message)
                    elif message.Headers:
                        msg = MIMEMultipart("mixed")
                        cs = charset.Charset("utf-8")
                        msg.set_charset(cs)

                        # Add headers
                        try:
                            folder_header = False
                            for key in message.Headers:
                                value = message.Headers[key]
                                msg[key] = value
                                if key == "X-Folder":
                                    folder_header = True
                            if message.Message_Path and folder_header is False:
                                msg["X-Folder"] = message.Message_Path
                        except Exception as e:
                            desc = "Error writing headers for MBOX derivative"
                            errors = helper.handle_error(errors, e, desc)

                        # Add message body
                        try:
                            if message.HTML_Body or message.Text_Body:
                                alt = MIMEMultipart("alternative")
                                if message.Text_Body:
                                    alt.attach(MIMEText(message.Text_Body, "plain", "utf-8"))
                                if message.HTML_Body:
                                    alt = MIMEMultipart("alternative")
                                    alt.attach(MIMEText(message.HTML_Body, "html", "utf-8"))
                                msg.attach(alt)
                            else:
                                desc = (
                                    "No body present for "
                                    + str(message.Mailbag_Message_ID)
                                    + ". Added message to MBOX without message body"
                                )
                                errors = helper.handle_error(errors, None, desc, "warn")
                        except Exception as e:
                            desc = "Error writing body for MBOX derivative"
                            errors = helper.handle_error(errors, e, desc)

                        # Attachments
                        try:
                            for attachment in message.Attachments:
                                mimeType = attachment.MimeType
                                if mimeType is None:
                                    mimeType = "text/plain"
                                    log.warn("Mime type not found for the attachment. Set as " + mimeType + ".")
                                mimeType = mimeType.split("/")
                                part = MIMEBase(mimeType[0], mimeType[1])
                                part.set_payload(attachment.File)
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", "attachment", filename=attachment.Name)
                                msg.attach(part)
                        except Exception as e:
                            desc = "Error writing attachment(s) to MBOX derivative"
                            errors = helper.handle_error(errors, e, desc)

                        mbox.add(msg)

                    else:
                        desc = "Unable to create MBOX as no body or headers present for " + str(message.Mailbag_Message_ID)
                        errors = helper.handle_error(errors, None, desc, "error")

                    mbox.flush()
                    mbox.unlock()

                except Exception as e:
                    desc = "Error writing MBOX derivative"
                    errors = helper.handle_error(errors, e, desc)

        except Exception as e:
            desc = "Error creating MBOX derivative"
            errors = helper.handle_error(errors, e, desc)

        message.Error.extend(errors["msg"])
        message.StackTrace.extend(errors["stack_trace"])

        return message
