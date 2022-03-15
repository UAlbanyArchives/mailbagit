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
            log.info("Reading :", File=self.file)

        def account_data(self):
            return account_data

        def folders(self, folder, path):
            # recursive function that calls itself on any subfolders and
            # returns a generator of messages
            # path is a list that you can create the filepath with os.path.join()
            if folder.number_of_sub_folders:
                path.append(folder.name)
                for folder_index in range(folder.number_of_sub_folders):
                    subfolder = folder.get_sub_folder(folder_index)
                    yield from self.folders(subfolder, path)
            if folder.number_of_sub_messages:
                log.debug("Reading folder: " + folder.name)
                path.append(folder.name)
                for index in range(folder.number_of_sub_messages):
                    
                    try:
                        messageObj = folder.get_sub_message(index)
                        headerParser = parser.HeaderParser()
                        headers = headerParser.parsestr(messageObj.transport_headers)
                        
                        attachmentNames = []
                        attachments = []
                        total_attachment_size_bytes = 0
                        for attachment in messageObj.attachments:
                            total_attachment_size_bytes = total_attachment_size_bytes + attachment.get_size()
                            attachment_content = attachment.read_buffer(attachment.get_size())
                            attachments.append(attachment_content)
                            attachmentNames.append(attachment.get_name())

                        message = Email(
                            Message_ID=headers['Message-ID'],
                            Email_Folder=os.path.join(*path),
                            Date=headers["Date"],
                            From=headers["From"],
                            To=headers["To"],
                            Cc=headers["To"],
                            Bcc=headers["Bcc"],
                            Subject=headers["Subject"],
                            Content_Type=headers["Content-Type"],
                            Headers=headers,
                            # detecting encoding might be problematic but works for now
                            Body=str(messageObj.html_body),
                            Text_Body=messageObj.plain_text_body.decode(chardet.detect(messageObj.plain_text_body)['encoding']),
                            HTML_Body=messageObj.html_body.decode(chardet.detect(messageObj.html_body)['encoding']),
                            AttachmentNum=int(messageObj.number_of_attachments),
                            Message=None,
                            AttachmentNames=attachmentNames,
                            AttachmentFiles=attachments,
                            Error='False'
                        )
                    
                    except (Exception) as e:
                        log.error(e)
                        message = Email(
                            Error='True'
                        )
                
                    # log.debug(message.to_struct())
                    yield message
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
                pst.open(self.file)
                root = pst.get_root_folder()
                count = 0
                for folder in root.sub_folders:
                    if folder.number_of_sub_folders:
                        return self.folders(folder, [])
                    else:
                        # gotta return empty directory to controller somehow
                        log.error("???--> " + folder.name)

                # Move PST to new mailbag directory structure
                new_path = helper.moveWithDirectoryStructure(self.dry_run,parent_dir,self.mailbag_name,self.format_name,subFolder,filePath)
