from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbox
import pypff


class PST(EmailAccount):
    # pst - This concrete class parses PST file format
    format_name = 'pst1'

    def __init__(self, target_account, **kwargs):
        print("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data


        self.file =target_account.input_path
        print("Reading :", self.file)
        pst = pypff.file()
        pst.open("self.file")

        self.data = pst.get_root_folder()

    def account_data(self):
        return account_data

    def messages(self):
        for folder in self.sub_folders:

                messages1 = []
                if folder.number_of_sub_folders:
                    messages1 += PST.messages(self=folder)
                for msg in folder.sub_messages:
                    message = {
                    #"Message_ID":msg.id,
                    "Email_Folder":msg.folder.name,
                    #"Date":msg.date,
                    "From":msg.sender_name,
                    #"To":msg.to,
                    #Cc":msg.cc,
                    #"Bcc":msg.bcc,
                    "Subject":msg.subject,
                    #"Content_Type":msg.content_type


                         }



        yield Email(**message)








