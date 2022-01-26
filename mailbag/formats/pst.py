from os.path import join
import mailbox
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email

log = get_logger()


class PST(EmailAccount):
    # pst - This concrete class parses PST file format
    format_name = 'pst'

    def __init__(self, dry_run, mailbag_name, target_account, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data

        self.file = target_account
        log.info("Reading :",File=self.file)

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
                    messageObj = folder.get_sub_message(index)
                    headerParser = parser.HeaderParser()
                    headers = headerParser.parsestr(messageObj.transport_headers)
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
                        Text_Body=messageObj.html_body,
                        HTML_Body=messageObj.plain_text_body,
                        Message=None
                    )
                    #log.debug(message.to_struct())
                    yield message
        else:
            # gotta return empty directory to controller somehow
            log.error("??--> " + folder.name)

    def messages(self):
        # only import libpff when PST is selected as the input format
        # this way it won't be required for parsing other formats
        import pypff

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
