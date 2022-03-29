import os, glob
import mailbox
import chardet
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email
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

        def folders(self, folder, path, original_filename):
            # recursive function that calls itself on any subfolders and
            # returns a generator of messages
            # path is a list that you can create the filepath with os.path.join()
            if folder.number_of_sub_messages:
                log.debug("Reading folder: " + folder.name)
                path.append(folder.name)
                for index in range(folder.number_of_sub_messages):
                    
                    error = []
                    try:
                        messageObj = folder.get_sub_message(index)

                        try:
                            headerParser = parser.HeaderParser()
                            headers = headerParser.parsestr(messageObj.transport_headers)
                        except Exception as e:
                            log.error(e)
                            error.append("Error parsing headers.")

                        try:
                            html_body = None
                            html_bytes = None
                            text_body = None
                            text_bytes = None
                            if messageObj.html_body:
                                html_bytes = messageObj.html_body
                                try:
                                    html_body = messageObj.html_body.decode(chardet.detect(messageObj.html_body)['encoding'])
                                except:
                                    pass
                            if messageObj.plain_text_body:
                                text_bytes = messageObj.plain_text_body
                                try:
                                    text_body = messageObj.plain_text_body.decode(chardet.detect(messageObj.plain_text_body)['encoding'])
                                except:
                                    pass
                        except Exception as e:
                            log.error(e)
                            error.append("Error parsing message body.")
                        
                        try:
                            attachmentNames = []
                            attachments = []
                            total_attachment_size_bytes = 0
                            for attachment in messageObj.attachments:
                                total_attachment_size_bytes = total_attachment_size_bytes + attachment.get_size()
                                attachment_content = attachment.read_buffer(attachment.get_size())
                                attachments.append(attachment_content)
                                attachmentNames.append(attachment.get_name())
                        except Exception as e:
                            log.error(e)
                            error.append("Error parsing attachments.")

                        message = Email(
                            Error=error,
                            Message_ID=headers['Message-ID'].strip(),
                            Message_Path=os.path.join(os.path.splitext(original_filename)[0], *path),
                            Original_Filename=original_filename,
                            Date=headers["Date"],
                            From=headers["From"],
                            To=headers["To"],
                            Cc=headers["To"],
                            Bcc=headers["Bcc"],
                            Subject=headers["Subject"],
                            Content_Type=headers.get_content_type(),
                            Headers=headers,
                            HTML_Bytes=html_bytes,
                            HTML_Body=html_body,
                            Text_Bytes=text_bytes,
                            Text_Body=text_body,
                            AttachmentNum=int(messageObj.number_of_attachments),
                            Message=None,
                            AttachmentNames=attachmentNames,
                            AttachmentFiles=attachments
                        )
                    
                    except (Exception) as e:
                        log.error(e)
                        message = Email(
                            Error=error.append('Error parsing message.')
                        )
                
                    # log.debug(message.to_struct())
                    yield message

            # iterate over any subfolders too       
            if folder.number_of_sub_folders:
                for folder_index in range(folder.number_of_sub_folders):
                    subfolder = folder.get_sub_folder(folder_index)
                    yield from self.folders(subfolder, path, original_filename)
            # else:
            #     # gotta return empty directory to controller somehow
            #     log.error("??--> " + folder.name)

        def messages(self):
            if os.path.isfile(self.file):
                files = self.file
                parent_dir = os.path.dirname(self.file)
            else:
                files = os.path.join(self.file, "**", "*.mbox")
                parent_dir = self.file
            file_list = glob.glob(files, recursive=True)

            for filePath in file_list:
                subFolder = helper.emailFolder(parent_dir, filePath)

                pst = pypff.file()
                pst.open(filePath)
                root = pst.get_root_folder()
                for folder in root.sub_folders:
                    if folder.number_of_sub_folders:
                        # call recursive function to parse email folder
                         yield from self.folders(folder, os.path.normpath(subFolder).split(os.sep), os.path.basename(filePath))
                    else:
                        # gotta return empty directory to controller somehow
                        log.error("???--> " + folder.name)
                pst.close()

                # Move PST to new mailbag directory structure
                mailbag_name = os.path.join(self.mailbag_name, "data")
                new_path = helper.moveWithDirectoryStructure(self.dry_run,parent_dir,mailbag_name,self.format_name,subFolder,filePath)
