from structlog import get_logger
import csv
from mailbag.email_account import EmailAccount
from mailbag.derivative import Derivative
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil, glob
import mailbag.helper as helper

log = get_logger()


class Controller:
    """Controller - Main controller"""

    def __init__(self, args):
        self.args = args
        self.format = self.format_map[args.input]
        self.derivatives_to_create = [self.derivative_map[d] for d in args.derivatives]

    @property
    def format_map(self):
        return EmailAccount.registry

    @property
    def derivative_map(self):
        return Derivative.registry

    def generate_mailbag(self):
        mail_account: EmailAccount = self.format(self.args.directory, self.args)

        derivatives = [d(mail_account) for d in self.derivatives_to_create]

        # do stuff you ought to do with per-account info here
        # mail_account.account_data()
        # for d in derivatives:
        # d.do_task_per_account()
        os.mkdir(os.path.join(self.args.directory, self.args.mailbag_name))
        files = os.path.join(self.args.directory, self.args.mailbag_name, "mailbag.csv")
        header = ['Mailbag-Message-ID', 'Message_ID', 'Email_Folder', 'Date', 'From', 'To', 'Cc', 'Bcc', 'Subject',
                  'Content_Type', 'Error']
        csv_data = []
        mailbag_message_id = 0
        csv_portion_count = 0
        csv_portion = []
        csv_portion.append(header)
        for message in mail_account.messages():
            # do stuff you ought to do per message here
            if csv_portion_count > 100000:
                mailbag_message_id = 1
                message.Mailbag_Message_ID = mailbag_message_id
                csv_data.append(csv_portion)
                csv_portion = []
                csv_portion.append(header)
                csv_portion.append(
                    [message.Mailbag_Message_ID, message.Message_ID, message.Email_Folder, message.Date, message.From,
                     message.To, message.Cc,message.Bcc, message.Subject, message.Content_Type, message.Error])
                csv_portion_count = 0
            else:
                mailbag_message_id += 1
                message.Mailbag_Message_ID = mailbag_message_id
                csv_portion.append(
                    [message.Mailbag_Message_ID, message.Message_ID, message.Email_Folder, message.Date, message.From,
                     message.To, message.Cc,message.Bcc, message.Subject, message.Content_Type, message.Error])
            csv_portion_count += 1

        csv_data.append(csv_portion)
        #if not self.args.dry_run:

        if len(csv_data) == 1:

                with open("mailbag.csv", 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(csv_data)
        else:
                portion_count = 0
                for portion in csv_data:
                    portion_count += 1
                    filename = "mailbag-" + str(portion_count) + ".csv"
                    with open(filename, 'w', encoding='UTF8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(portion)

        for message in mail_account.messages():
        # do stuff you ought to do per message here
            for d in derivatives:
                        d.do_task_per_message(message)

        return mail_account.messages()
