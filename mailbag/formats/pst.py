from os.path import join
import mailbox
import chardet
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email

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
            # path is a list that you can create the filepath with join()
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
                        if messageObj.number_of_attachments > 0:
                            total_attachment_size_bytes = 0
                            for i in range(messageObj.number_of_attachments):
                                total_attachment_size_bytes = total_attachment_size_bytes + (messageObj.get_attachment(i)).get_size()
                                # attachment_content = ((messageObj.get_attachment(i)).read_buffer((messageObj.get_attachment(i)).get_size())).decode('ascii',errors="ignore")
                                attachment_content = (messageObj.get_attachment(i)).read_buffer((messageObj.get_attachment(i)).get_size())
                                attachments.append(attachment_content)
                                attachmentNames.append(messageObj.get_attachment(i).get_name())

                        message = Email(
                            Message_ID=headers['Message-ID'],
                            Email_Folder=join(*path),
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
                            # Text_Body=messageObj.plain_text_body.decode(chardet.detect(messageObj.plain_text_body)['encoding']),
                            # HTML_Body=messageObj.html_body.decode(chardet.detect(messageObj.html_body)['encoding']),
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
