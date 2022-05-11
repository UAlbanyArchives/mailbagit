# This is Eml derivative
from os.path import join
import mailbag.helper as helper
import os, glob
import mailbox
from mailbag.email_account import EmailAccount
from structlog import get_logger
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, charset
from email import generator
from mailbag.derivative import Derivative
import platform


log = get_logger()


class EmlDerivative(Derivative):
    derivative_name = "eml"
    derivative_format = "eml"
    derivative_agent = email.__name__
    derivative_agent_version = platform.python_version()

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.eml_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.eml_dir)

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message):

        errors = {}
        errors["msg"] = []
        errors["stack_trace"] = []

        try:

            out_dir = os.path.join(self.eml_dir, message.Derivatives_Path)
            filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))

            # Build msg
            if not message.Message and not message.Headers:
                desc = "Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID)
                errors = helper.handle_error(errors, None, desc, "error")
            else:
                fullObjectWrite = False
                if message.Message:
                    msg = message.Message
                    # Try to write full EML to disk
                    if message.HTML_Encoding:
                        out_encoding = message.HTML_Encoding
                    elif message.Text_Encoding:
                        out_encoding = message.Text_Encoding
                    else:
                        out_encoding = "utf-8"
                    log.debug("Writing full EML object to " + str(out_dir))
                    try:
                        if not self.args.dry_run:
                            if not os.path.isdir(out_dir):
                                os.makedirs(out_dir)
                            with open(filename + ".eml", "w", encoding=out_encoding) as outfile:
                                gen = generator.Generator(outfile)
                                gen.flatten(msg)
                                outfile.close()
                            fullObjectWrite = True
                    except Exception as e:
                        helper.deleteFile(filename + ".eml")
                        desc = "Error writing full email object to EML, generating it from the model instead"
                        errors = helper.handle_error(errors, e, desc, "warn")
                        fullObjectWrite = False

                if fullObjectWrite == False:
                    if message.Headers:
                        msg = MIMEMultipart("mixed")
                        cs = charset.Charset("utf-8")
                        msg.set_charset(cs)

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
                            desc = "Error writing headers for EML derivative"
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
                                desc = "No body present for " + str(message.Mailbag_Message_ID) + ". Created EML without message body"
                                errors = helper.handle_error(errors, None, desc, "warn")
                        except Exception as e:
                            desc = "Error writing body for EML derivative"
                            errors = helper.handle_error(errors, e, desc)

                        # Attachments
                        try:
                            for attachment in message.Attachments:
                                mimeType = attachment.MimeType
                                if mimeType is None:
                                    mimeType = "text/plain"
                                    desc = "Mime type not found for attachment, set as " + mimeType
                                    errors = helper.handle_error(errors, None, desc, "warn")
                                mimeType = mimeType.split("/")
                                part = MIMEBase(mimeType[0], mimeType[1])
                                part.set_payload(attachment.File)
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", "attachment", filename=attachment.Name)
                                msg.attach(part)
                        except Exception as e:
                            desc = "Error writing attachment(s) to EML derivative"
                            errors = helper.handle_error(errors, e, desc)

                        # Write generated EML to disk
                        log.debug("Writing generated EML to " + str(out_dir))
                        try:
                            if not self.args.dry_run:
                                if not os.path.isdir(out_dir):
                                    os.makedirs(out_dir)
                                with open(filename + ".eml", "w", encoding="utf-8") as outfile:
                                    gen = generator.Generator(outfile)
                                    gen.flatten(msg)
                                    outfile.close()
                        except Exception as e:
                            desc = "Error writing EML derivative"
                            errors = helper.handle_error(errors, e, desc)

                    else:
                        desc = "Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID)
                        errors = helper.handle_error(errors, None, desc, "error")

        except Exception as e:
            desc = "Error creating EML derivative"
            errors = helper.handle_error(errors, e, desc)

        message.Error.extend(errors["msg"])
        message.StackTrace.extend(errors["stack_trace"])

        return message
