import os
import email
from pathlib import Path
import chardet
from extract_msg.constants import CODE_PAGES
from mailbagit.loggerx import get_logger
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

        def __init__(self, args, parent_dir, mailbag_dir, mailbag_name, **kwargs):
            log.debug("Parsity parse")
            # code goes here to set up mailbox and pull out any relevant account_data
            self._account_data = {}
            self.path = args.path
            self.dry_run = args.dry_run
            self.keep = args.keep
            self.mailbag_name = mailbag_name
            self.mailbag_dir = mailbag_dir
            self.parent_dir = parent_dir
            self.companion_files = args.companion_files
            log.info("Reading: " + self.path)

        @property
        def account_data(self):
            return self._account_data

        @property
        def number_of_messages(self):
            count = 0
            for _ in self.messages(iteration_only=True):
                count += 1
            return count

        def folders(self, folder, path, originalFile, iteration_only=False):
            # recursive function that calls itself on any subfolders and
            # returns a generator of messages
            # path is the email folder path of the message, separated by "/"
            if folder.number_of_sub_messages:
                log.debug("Reading folder: " + folder.name)
                for index in range(folder.number_of_sub_messages):

                    if iteration_only:
                        yield None
                        continue
                    attachments = []
                    errors = []
                    try:
                        messageObj = folder.get_sub_message(index)

                        try:
                            headerParser = email.parser.HeaderParser()
                            if messageObj.transport_headers:
                                headers = headerParser.parsestr(messageObj.transport_headers)
                            else:
                                # often returns none for deleted and sent items in OSTs
                                desc = "Unable to read headers. An empty headers object will be created."
                                errors = common.handle_error(errors, None, desc)
                                # just make an empty object
                                headers = headerParser.parsestr("headers: not found")
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
                            # messageObj.html_body sometimes fails. This seems to often be the case for email in "Deleted Items"
                            try:
                                if messageObj.html_body:
                                    html_body, html_encoding, errors = format.safely_decode("HTML", messageObj.html_body, encodings, errors)
                            except:
                                pass
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
                            derivativesPath = Path(os.path.splitext(originalFile)[0], common.normalizePath(messagePath)).as_posix()
                        except Exception as e:
                            desc = "Error reading message path"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            total_attachment_size_bytes = 0
                            for i, attachmentObj in enumerate(messageObj.attachments):
                                total_attachment_size_bytes = total_attachment_size_bytes + attachmentObj.get_size()
                                attachment_content = attachmentObj.read_buffer(attachmentObj.get_size())

                                attachmentName = None
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
                                            attachmentWrittenName = str(i) + os.path.splitext(attachmentName)[1]
                                        else:
                                            attachmentWrittenName = common.normalizePath(attachmentName.replace("/", "%2F"))
                                    else:
                                        attachmentWrittenName = str(i)

                                    # Guess the mime if we can't find it
                                    if mime is None:
                                        if attachmentName:
                                            mime = format.guessMimeType(attachmentName)
                                        else:
                                            desc = "Mimetype not found. Setting it to 'application/octet-stream'"
                                            errors = common.handle_error(errors, None, desc, "warn")
                                            mime = "application/octet-stream"

                                    # MSGs & PSTs don't seem to have a reliable content ID so we make one since emails may have multiple attachments with the same filename
                                    contentID = uuid.uuid4().hex

                                except Exception as e:
                                    attachmentName = str(len(attachments))
                                    desc = (
                                        "No filename found for attachment " + attachmentName + " for message " + str(headers["Message-ID"])
                                    )
                                    errors = common.handle_error(errors, e, desc)

                                attachment = Attachment(
                                    Name=attachmentName,
                                    WrittenName=attachmentWrittenName,
                                    File=attachment_content,
                                    MimeType=mime,
                                    Content_ID=contentID,
                                )
                                attachments.append(attachment)

                        except Exception as e:
                            desc = "Error parsing attachments"
                            errors = common.handle_error(errors, e, desc)

                        decoded_Message_ID, errors = format.parse_header(headers["Message-ID"], errors)
                        decoded_Date, errors = format.parse_header(headers["Date"], errors)
                        decoded_From, errors = format.parse_header(headers["From"], errors)
                        decoded_To, errors = format.parse_header(headers["To"], errors)
                        decoded_Cc, errors = format.parse_header(headers["Cc"], errors)
                        decoded_Bcc, errors = format.parse_header(headers["Bcc"], errors)
                        decoded_Subject, errors = format.parse_header(headers["Subject"], errors)

                        message = Email(
                            Errors=errors,
                            Message_ID=decoded_Message_ID,
                            Original_File=originalFile,
                            Message_Path=messagePath,
                            Derivatives_Path=derivativesPath,
                            Date=decoded_Date,
                            From=decoded_From,
                            To=decoded_To,
                            Cc=decoded_Cc,
                            Bcc=decoded_Bcc,
                            Subject=decoded_Subject,
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
                    yield from self.folders(subfolder, path + "/" + subfolder.name, originalFile, iteration_only=iteration_only)
            else:
                if not iteration_only:
                    if not folder.number_of_sub_messages:
                        # This is an email folder that does not contain any messages.
                        # Add it to self.account_data['empty_folder_paths']
                        if not "empty_folder_paths" in self.account_data:
                            self.account_data["empty_folder_paths"] = []
                        self.account_data["empty_folder_paths"].append(os.path.splitext(originalFile)[0] + "/" + path)

        def messages(self, iteration_only=False):
            companion_files = []
            if os.path.isfile(self.path):
                fileList = [self.path]
            else:
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
                        yield from self.folders(folder, folder.name, originalFile, iteration_only=iteration_only)
                    else:
                        if not iteration_only:
                            # This is an email folder that does not contain any messages.
                            # Add it to self.account_data['empty_folder_paths']
                            if not "empty_folder_paths" in self.account_data:
                                self.account_data["empty_folder_paths"] = []
                            self.account_data["empty_folder_paths"].append(os.path.splitext(originalFile)[0] + "/" + folder.name)
                pst.close()

                # Move PST to new mailbag directory structure
                if not iteration_only:
                    new_path, errors = format.moveWithDirectoryStructure(
                        self.dry_run,
                        self.keep,
                        self.parent_dir,
                        self.mailbag_dir,
                        self.mailbag_name,
                        self.format_name,
                        filePath,
                        # Does not check path lengths for PSTs
                        [],
                    )

            if self.companion_files:
                # Move all files into mailbag directory structure
                for companion_file in companion_files:
                    new_path = format.moveWithDirectoryStructure(
                        self.dry_run, self.keep, self.parent_dir, self.mailbag_dir, self.mailbag_name, self.format_name, companion_file
                    )
