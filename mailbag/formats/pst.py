from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbox
import pypff


class PST(EmailAccount):
    # pst - This concrete class parses PST file format
    format_name = 'pst'

    def __init__(self, target_account, **kwargs):
        print("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data


        self.file =target_account.input_path
        print("Reading :", self.file)







    def account_data(self):
        return account_data

    def parse_folder(root):
        messages=[]

        for folder in root.sub_folders:
            if folder.number_of_sub_folders:
                messages += PST.parse_folder(folder)


            for message in folder.sub_messages:
                messages.append({
                    "subject": message.subject,
                    "sender": message.sender_name,
                    "Folder":folder.name

                })

        return messages

    def messages(self):
        pst = pypff.file()
        pst.open(self.file)
        root = pst.get_root_folder()
        m=PST.parse_folder(root)
        for att in m:
            message = {
                #"Message_ID": i['Message-ID'],
                "Email_Folder": att["Folder"],
               # "Date": i["Creationtime"],
                "From": att["sender"],
               # "To": i["To"],
               # "Cc": i["CC"],
               # "Bcc": i['Bcc'],
                "Subject": att["subject"],
                #"Content_Type": i['Content-Type']
            }

            yield Email(**message)








