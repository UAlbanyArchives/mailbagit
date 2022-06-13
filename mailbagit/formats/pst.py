import os
import mailbox
from pathlib import Path
import chardet
from extract_msg.constants import CODE_PAGES
from mailbagit.loggerx import get_logger
from email import parser
from mailbagit.email_account import EmailAccount
from mailbagit.models import Email, Attachment
import mailbagit.helper.format as format
import mailbagit.helper.common as common
import uuid

# only create format if pypff is successfully importable -
# pst is not supported otherwise
skip_registry = False
try:
    import pypff
except:
    skip_registry = True

log = get_logger()

if not skip_registry:

    class PST(EmailAccount):
        # pst - This concrete class parses PST file format
        format_name = "pst"
        try:
            from importlib import metadata
        except ImportError:  # for Python<3.8
            import importlib_metadata as metadata
        format_agent = pypff.__name__
        format_agent_version = metadata.version("libpff-python")

        def __init__(self, target_account, args, **kwargs):
            log.debug("Parsity parse")
            # code goes here to set up mailbox and pull out any relevant account_data

            self.path = target_account
            self.dry_run = args.dry_run
            self.mailbag_name = args.mailbag_name
            self.companion_files = args.companion_files
            self.iteration_only = False
            log.info("Reading :", Path=self.path)

        def account_data(self):
            return account_data

        def folders(self, folder, path, originalFile):
            # recursive function that calls itself on any subfolders and
            # returns a generator of messages
            # path is the email folder path of the message, separated by "/"
            if folder.number_of_sub_messages:
                log.debug("Reading folder: " + folder.name)
                for index in range(folder.number_of_sub_messages):

                    if self.iteration_only:
                        yield None
                        continue
                    attachments = []
                    errors = []
                    try:
                        messageObj = folder.get_sub_message(index)

                        try:
                            headerParser = parser.HeaderParser()
                            headers = headerParser.parsestr(messageObj.transport_headers)
                        except Exception as e:
                            desc = "Error parsing message body"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            # Parse message bodies
                            html_body = None
                            text_body = None
                            html_encoding = None
                            text_encoding = None

                            # Codepage integers found here: https://github.com/libyal/libpff/blob/main/libpff/libpff_mapi.h#L333-L335
                            # Docs say to use MESSAGE_CODEPAGE: https://github.com/libyal/libfmapi/blob/main/documentation/MAPI%20definitions.asciidoc#51-the-message-body
                            # this is a 32bit encoded integer
                            encodings = {}
                            LIBPFF_ENTRY_TYPE_MESSAGE_BODY_CODEPAGE = int("0x3fde", base=16)
                            LIBPFF_ENTRY_TYPE_MESSAGE_CODEPAGE = int("0x3ffd", base=16)
                            for record_set in messageObj.record_sets:
                                for entry in record_set.entries:
                                    if entry.entry_type == LIBPFF_ENTRY_TYPE_MESSAGE_BODY_CODEPAGE:
                                        if entry.data:
                                            value = entry.get_data_as_integer()
                                            # Use the extract_msg code page in constants.py
                                            encodings[1] = {"name": CODE_PAGES[value], "label": "PidTagInternetCodepage"}
                                    if entry.entry_type == LIBPFF_ENTRY_TYPE_MESSAGE_CODEPAGE:
                                        if entry.data:
                                            value = entry.get_data_as_integer()
                                            # Use the extract_msg code page in constants.py
                                            encodings[2] = {"name": CODE_PAGES[value], "label": "PidTagMessageCodepage"}

                            if messageObj.html_body:
                                html_body, html_encoding, errors = format.safely_decode("HTML", messageObj.html_body, encodings, errors)
                            if messageObj.plain_text_body:
                                encodings[len(encodings.keys()) + 1] = {
                                    "name": "utf-8",
                                    "label": "manual",
                                }
                                encodings[len(encodings.keys()) + 2] = {
                                    "name": chardet.detect(messageObj.plain_text_body)["encoding"],
                                    "label": "detected",
                                }
                                text_body, text_encoding, errors = format.safely_decode(
                                    "plain text", messageObj.plain_text_body, encodings, errors
                                )

                        except Exception as e:
                            desc = "Error parsing message body"
                            errors = common.handle_error(errors, e, desc)

                        # Build message and derivatives paths
                        try:
                            messagePath = path
                            if len(messagePath) > 0:
                                messagePath = Path(messagePath).as_posix()
                            derivativesPath = Path(os.path.splitext(originalFile)[0], format.normalizePath(messagePath)).as_posix()
                        except Exception as e:
                            desc = "Error reading message path"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            total_attachment_size_bytes = 0
                            for attachmentObj in messageObj.attachments:
                                total_attachment_size_bytes = total_attachment_size_bytes + attachmentObj.get_size()
                                attachment_content = attachmentObj.read_buffer(attachmentObj.get_size())

                                try:
                                    # attachmentName = attachmentObj.get_name()
                                    # Entries found here: https://github.com/libyal/libpff/blob/main/libpff/libpff_mapi.h#L333-L335
                                    LIBPFF_ENTRY_TYPE_ATTACHMENT_FILENAME_LONG = int("0x3707", base=16)
                                    LIBPFF_ENTRY_TYPE_ATTACHMENT_FILENAME_SHORT = int("0x3704", base=16)
                                    LIBPFF_ENTRY_TYPE_ATTACHMENT_MIME_TAG = int("0x370e", base=16)
                                    attachmentLong = ""
                                    attachmentShort = ""
                                    mime = None
                                    for record_set in attachmentObj.record_sets:
                                        for entry in record_set.entries:
                                            if entry.entry_type == LIBPFF_ENTRY_TYPE_ATTACHMENT_FILENAME_LONG:
                                                if entry.data:
                                                    attachmentLong = entry.get_data_as_string()
                                            if entry.entry_type == LIBPFF_ENTRY_TYPE_ATTACHMENT_FILENAME_SHORT:
                                                if entry.data:
                                                    attachmentShort = entry.get_data_as_string()
                                            if entry.entry_type == LIBPFF_ENTRY_TYPE_ATTACHMENT_MIME_TAG:
                                                if entry.data:
                                                    mime = entry.get_data_as_string()
                                    # Use the Long filename preferably
                                    if len(attachmentLong) > 0:
                                        attachmentName = attachmentLong
                                    elif len(attachmentShort) > 0:
                                        attachmentName = attachmentShort
                                    else:
                                        attachmentName = None
                                        desc = "No filename found for attachment, integer will be used instead"
                                        errors = common.handle_error(errors, None, desc)

                                    # Handle attachments.csv conflict
                                    # helper.controller.writeAttachmentsToDisk() handles this
                                    if attachmentName:
                                        if attachmentName.lower() == "attachments.csv":
                                            desc = (
                                                "attachment "
                                                + attachmentName
                                                + " will be renamed to avoid filename conflict with mailbag spec"
                                            )
                                            errors = common.handle_error(errors, None, desc, "warn")

                                    # Guess the mime if we can't find it
                                    if mime is None:
                                        mime = format.guessMimeType(attachmentName)

                                    # MSGs don't seem to have a reliable content ID so we make one since emails may have multiple attachments with the same filename
                                    contentID = uuid.uuid4().hex

                                except Exception as e:
                                    attachmentName = str(len(attachments))
                                    desc = (
                                        "No filename found for attachment " + attachmentName + " for message " + str(headers["Message-ID"])
                                    )
                                    errors = common.handle_error(errors, e, desc)

                                attachment = Attachment(
                                    Name=attachmentName,
                                    File=attachment_content,
                                    MimeType=mime,
                                    Content_ID=contentID,
                                )
                                attachments.append(attachment)

                        except Exception as e:
                            desc = "Error parsing attachments"
                            errors = common.handle_error(errors, e, desc)

                        message = Email(
                            Errors=errors,
                            Message_ID=format.parse_header(headers["Message-ID"]),
                            Original_File=originalFile,
                            Message_Path=messagePath,
                            Derivatives_Path=derivativesPath,
                            Date=format.parse_header(headers["Date"]),
                            From=format.parse_header(headers["From"]),
                            To=format.parse_header(headers["To"]),
                            Cc=format.parse_header(headers["Cc"]),
                            Bcc=format.parse_header(headers["Bcc"]),
                            Subject=format.parse_header(headers["Subject"]),
                            Content_Type=headers.get_content_type(),
                            Headers=headers,
                            HTML_Body=html_body,
                            HTML_Encoding=html_encoding,
                            Text_Body=text_body,
                            Text_Encoding=text_encoding,
                            Message=None,
                            Attachments=attachments,
                        )

                    except (Exception) as e:
                        desc = "Error parsing message"
                        errors = common.handle_error(errors, e, desc)
                        message = Email(Errors=errors)

                    yield message

            # iterate over any subfolders too
            if folder.number_of_sub_folders:
                for folder_index in range(folder.number_of_sub_folders):
                    subfolder = folder.get_sub_folder(folder_index)
                    yield from self.folders(subfolder, path + "/" + subfolder.name, originalFile)
            else:
                if not self.iteration_only:
                    if not folder.number_of_sub_messages:
                        # This is an email folder that does not contain any messages.
                        # Currently, we are only warning about empty folders pending the possibility of
                        # a better solution described in #117
                        desc = "Folder '" + path + "' contains no messages and will be ignored"
                        # handle_error() won't work here as-is because the errors list is added to the Message model
                        # errors = common.handle_error(errors, None, desc, "warn")
                        log.warn(desc + ".")

        def messages(self):
            companion_files = []
            if os.path.isfile(self.path):
                parent_dir = os.path.dirname(self.path)
                fileList = [self.path]
            else:
                parent_dir = self.path
                fileList = []
                for root, dirs, files in os.walk(self.path):
                    for file in files:
                        mailbag_path = os.path.join(self.path, self.mailbag_name) + os.sep
                        fileRoot = root + os.sep
                        # don't count the newly-created mailbag
                        if not fileRoot.startswith(mailbag_path):
                            if file.lower().endswith("." + self.format_name):
                                fileList.append(os.path.join(root, file))
                            elif self.companion_files:
                                companion_files.append(os.path.join(root, file))

            for filePath in fileList:
                rel_path = format.relativePath(self.path, filePath)  # returns "" when path is a file
                if len(rel_path) < 1:
                    originalFile = Path(filePath).name
                else:
                    originalFile = Path(os.path.normpath(rel_path)).as_posix()
                # original file is now the relative path to the PST from the provided path

                pst = pypff.file()
                pst.open(filePath)
                root = pst.get_root_folder()
                for folder in root.sub_folders:
                    if folder.number_of_sub_folders:
                        # call recursive function to parse email folder
                        yield from self.folders(folder, folder.name, originalFile)
                    else:
                        if not self.iteration_only:
                            # This is an email folder that does not contain any messages.
                            # Currently, we are only warning about empty folders pending the possibility of
                            # a better solution described in #117
                            desc = "Folder '" + folder.name + "' contains no messages and will be ignored"
                            # handle_error() won't work here as-is because the errors list is added to the Message model
                            # errors = common.handle_error(errors, None, desc, "warn")
                            log.warn(desc + ".")

                pst.close()

                # Move PST to new mailbag directory structure
                if not self.iteration_only:
                    new_path = format.moveWithDirectoryStructure(
                        self.dry_run,
                        parent_dir,
                        self.mailbag_name,
                        self.format_name,
                        filePath,
                    )

            if self.companion_files:
                # Move all files into mailbag directory structure
                for companion_file in companion_files:
                    new_path = format.moveWithDirectoryStructure(
                        self.dry_run, self.path, self.mailbag_name, self.format_name, companion_file
                    )
