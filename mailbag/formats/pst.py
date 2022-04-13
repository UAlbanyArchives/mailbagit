import os, glob
import mailbox

import chardet
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email, Attachment
import mailbag.helper as helper

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
        format_name = 'pst'

        def __init__(self, target_account, args, **kwargs):
            log.debug("Parsity parse")
            # code goes here to set up mailbox and pull out any relevant account_data

            self.file = target_account
            self.dry_run = args.dry_run
            self.mailbag_name = args.mailbag_name
            log.info("Reading :", File=self.file)

        def account_data(self):
            return account_data

        def folders(self, folder, path, originalFile):
            # recursive function that calls itself on any subfolders and
            # returns a generator of messages
            # path is a list that you can create the filepath with os.path.join()
            if folder.number_of_sub_messages:
                log.debug("Reading folder: " + folder.name)
                path.append(folder.name)
                for index in range(folder.number_of_sub_messages):

                    attachments = []
                    errors = {}
                    errors["msg"] = []
                    errors["stack_trace"] = []
                    try:
                        messageObj = folder.get_sub_message(index)

                        try:
                            headerParser = parser.HeaderParser()
                            headers = headerParser.parsestr(messageObj.transport_headers)
                        except Exception as e:
                            desc = "Error parsing message body"
                            errors = helper.handle_error(errors, e, desc)


                        try:
                            # Parse message bodies
                            html_body = None
                            text_body = None
                            html_encoding = None
                            text_encoding = None
                            if messageObj.html_body:
                                html_encoding = chardet.detect(messageObj.html_body)['encoding']
                                html_body = messageObj.html_body.decode(html_encoding)
                            if messageObj.plain_text_body:
                                text_encoding = chardet.detect(messageObj.plain_text_body)['encoding']
                                text_body = messageObj.plain_text_body.decode(text_encoding)
                        except Exception as e:
                            desc = "Error parsing message body"
                            errors = helper.handle_error(errors, e, desc)

                        # Build message and derivatives paths
                        try:
                            messagePath = os.path.join(os.path.splitext(originalFile)[0], *path)
                            derivativesPath = helper.normalizePath(messagePath)
                        except Exception as e:
                            desc = "Error reading message path"
                            errors = helper.handle_error(errors, e, desc)
                        
                        try:
                            total_attachment_size_bytes = 0
                            for attachmentObj in messageObj.attachments:
                                total_attachment_size_bytes = total_attachment_size_bytes + attachmentObj.get_size()
                                attachment_content = attachmentObj.read_buffer(attachmentObj.get_size())

                                try:
                                    attachmentName = attachmentObj.get_name()
                                except:
                                    attachmentName = str(len(attachments))
                                    desc = "No filename found for attachment " + attachmentName + \
                                    " for message " + str(message.Mailbag_Message_ID)
                                    errors = helper.handle_error(errors, e, desc)
                                
                                attachment = Attachment(
                                                        Name=attachmentName,
                                                        File=attachment_content,
                                                        MimeType=helper.guessMimeType(attachmentName)
                                            )
                                attachments.append(attachment)
                                
                        except Exception as e:
                            desc = "Error parsing attachments"
                            errors = helper.handle_error(errors, e, desc)


                        message = Email(
                            Error=errors["msg"],
                            Message_ID=headers['Message-ID'].strip(),
                            Original_File=originalFile,
                            Message_Path=messagePath,
                            Derivatives_Path=derivativesPath,
                            Date=headers["Date"],
                            From=headers["From"],
                            To=headers["To"],
                            Cc=headers["Cc"],
                            Bcc=headers["Bcc"],
                            Subject=headers["Subject"],
                            Content_Type=headers.get_content_type(),
                            Headers=headers,
                            HTML_Body=html_body,
                            HTML_Encoding=html_encoding,
                            Text_Body=text_body,
                            Text_Encoding=text_encoding,
                            Message=None,
                            Attachments=attachments,
                            StackTrace=errors["stack_trace"]
                        )
                
                    except (Exception) as e:
                        desc = 'Error parsing message'
                        errors = helper.handle_error(errors, e, desc)
                        message = Email(
                            Error=errors["msg"],
                            StackTrace=errors["stack_trace"]
                        )
                
                    yield message

            # iterate over any subfolders too       
            if folder.number_of_sub_folders:
                for folder_index in range(folder.number_of_sub_folders):
                    subfolder = folder.get_sub_folder(folder_index)
                    yield from self.folders(subfolder, path, originalFile)
            # else:
            #     # gotta return empty directory to controller somehow
            #     log.error("??--> " + folder.name)

        def messages(self):
            if os.path.isfile(self.file):
                files = self.file
                parent_dir = os.path.dirname(self.file)
            else:
                files = os.path.join(self.file, "**", "*.pst")
                parent_dir = self.file
            file_list = glob.glob(files, recursive=True)

            for filePath in file_list:
                originalFile = helper.relativePath(self.file, filePath)
                if len(originalFile) < 1:
                    pathList = []
                else:
                    pathList = os.path.normpath(originalFile).split(os.sep)

                pst = pypff.file()
                pst.open(filePath)
                root = pst.get_root_folder()
                for folder in root.sub_folders:
                    if folder.number_of_sub_folders:
                        # call recursive function to parse email folder
                         yield from self.folders(folder, pathList, os.path.basename(filePath))
                    else:
                        # gotta return empty directory to controller somehow
                        log.error("???--> " + folder.name)
                pst.close()

                # Move PST to new mailbag directory structure
                new_path = helper.moveWithDirectoryStructure(self.dry_run,parent_dir,self.mailbag_name,self.format_name,filePath)
