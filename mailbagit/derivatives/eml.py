# This is Eml derivative
from os.path import join
import mailbagit.helper.common as common
import mailbagit.helper.derivative as derivative
import os, glob
import mailbox
from mailbagit.email_account import EmailAccount
from mailbagit.loggerx import get_logger
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, charset
from email import generator
from mailbagit.derivative import Derivative
import platform


log = get_logger()


class EmlDerivative(Derivative):
    derivative_name = "eml"
    derivative_format = "eml"
    derivative_agent = "email"
    derivative_agent_version = platform.python_version()

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
            filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".eml")
            errors = common.check_path_length(out_dir, errors)
            errors = common.check_path_length(filename, errors)

            # Build msg
            if not message.Message and not message.Headers:
                desc = "Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID)
                errors = common.handle_error(errors, None, desc, "error")
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
                            with open(filename, "w", encoding=out_encoding) as outfile:
                                gen = generator.Generator(outfile)
                                gen.flatten(msg)
                                outfile.close()
                            fullObjectWrite = True
                    except Exception as e:
                        derivative.deleteFile(filename)
                        desc = "Error writing full email object to EML, generating it from the model instead"
                        errors = common.handle_error(errors, e, desc, "warn")
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
                            errors = common.handle_error(errors, e, desc)

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
                                errors = common.handle_error(errors, None, desc, "warn")
                        except Exception as e:
                            desc = "Error writing body for EML derivative"
                            errors = common.handle_error(errors, e, desc)

                        # Get list of <img> files that might reference attachments
                        if message.HTML_Body:
                            inline_files = derivative.inlineAttachments(message.HTML_Body, message.HTML_Encoding)
                        else:
                            inline_files = {}

                        # Attachments
                        try:
                            for attachment in message.Attachments:
                                mimeType = attachment.MimeType
                                if mimeType is None:
                                    mimeType = "application/octet-stream"
                                    desc = "Mime type not found for attachment, set as " + mimeType
                                    errors = common.handle_error(errors, None, desc, "error")
                                mimeType = mimeType.split("/")
                                part = MIMEBase(mimeType[0], mimeType[1])
                                part.set_payload(attachment.File)
                                encoders.encode_base64(part)

                                # Check if the attachment is inline in the HTML
                                if attachment.Content_ID in inline_files.values():
                                    content_disposition = "inline"
                                    part.add_header("Content-ID", attachment.Content_ID)
                                elif attachment.Name in inline_files.keys():
                                    # If the source was MSG or PST, we generated attachment.Content_ID so it won't match
                                    content_disposition = "inline"
                                    part.add_header("Content-ID", "<" + inline_files[attachment.Name] + ">")
                                else:
                                    content_disposition = "attachment"
                                    part.add_header("Content-ID", attachment.Content_ID)

                                part.add_header("Content-Disposition", content_disposition, filename=attachment.Name)
                                msg.attach(part)
                        except Exception as e:
                            desc = "Error writing attachment(s) to EML derivative"
                            errors = common.handle_error(errors, e, desc)

                        # Write generated EML to disk
                        log.debug("Writing generated EML to " + str(out_dir))
                        try:
                            if not self.args.dry_run:
                                if not os.path.isdir(out_dir):
                                    os.makedirs(out_dir)
                                with open(filename, "w", encoding="utf-8") as outfile:
                                    gen = generator.Generator(outfile)
                                    gen.flatten(msg)
                                    outfile.close()
                        except Exception as e:
                            desc = "Error writing EML derivative"
                            errors = common.handle_error(errors, e, desc)

                    else:
                        desc = "Unable to create EML as no body or headers present for " + str(message.Mailbag_Message_ID)
                        errors = common.handle_error(errors, None, desc, "error")

        except Exception as e:
            desc = "Error creating EML derivative"
            errors = common.handle_error(errors, e, desc)

        message.Errors.extend(errors)

        return message
