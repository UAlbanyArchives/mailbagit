import bagit
from structlog import get_logger
import csv
from mailbag.email_account import EmailAccount
from mailbag.derivative import Derivative
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil, glob
import mailbag.helper as helper

import traceback
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
        #for d in derivatives:
        #    d.do_task_per_account()

        #Create folder mailbag folder before writing mailbag.csv
        if os.path.isfile(self.args.directory):
            parent_dir = os.path.dirname(self.args.directory)
        else:
            parent_dir = self.args.directory
        mailbag_dir = os.path.join(parent_dir, self.args.mailbag_name)
        attachments_dir = os.path.join(str(mailbag_dir),'data','attachments')
        error_dir=os.path.join(parent_dir,str(self.args.mailbag_name)+'_errors')
        log.debug("Creating mailbag at " + str(mailbag_dir))

        if not self.args.dry_run:
            os.mkdir(mailbag_dir)
            # Creating a bagit-python style bag
            bag = bagit.make_bag(mailbag_dir)
            os.mkdir(attachments_dir)


        #Setting up mailbag.csv
        header = ['Error', 'Mailbag-Message-ID', 'Message-ID', 'Message-Path', 'Original-Filename','Date', 'From', 'To', 'Cc', 'Bcc', 'Subject',
                  'Content_Type']
        csv_data = []
        mailbag_message_id = 0
        csv_portion_count = 0
        csv_portion = []
        csv_portion.append(header)
        error_csv = []
        error_header = [ 'Mailbag-Message-ID','Original_Filename','Error']
        error_csv.append(error_header)


        for message in mail_account.messages():
            # do stuff you ought to do per message here

            # Generate mailbag_message_id
            mailbag_message_id += 1
            message.Mailbag_Message_ID = mailbag_message_id
            
            if message.AttachmentNum and message.AttachmentNum>0:
                helper.saveAttachmentOnDisk(self.args.dry_run,attachments_dir,message)
            
            # Setting up CSV data
            # checking if the count of messages exceed 100000 and creating a new portion if it exceeds
            if csv_portion_count > 100000:
                csv_data.append(csv_portion)
                csv_portion = []
                csv_portion.append(header)
                csv_portion.append(
                    [" ".join(message.Error), message.Mailbag_Message_ID, message.Message_ID, message.Message_Path, message.Original_Filename, message.Date, message.From,
                     message.To, message.Cc,message.Bcc, message.Subject, message.Content_Type])
                csv_portion_count = 0
            #if count is less than 100000 , appending the messages in one list
            else:
                csv_portion.append(
                    [" ".join(message.Error), message.Mailbag_Message_ID, message.Message_ID, message.Message_Path, message.Original_Filename, message.Date, message.From,
                     message.To, message.Cc,message.Bcc, message.Subject, message.Content_Type])
            csv_portion_count += 1

            #creating text file filr and csv if error is present
            if len(message.Error) > 0:
                if not os.path.isdir(error_dir):
                    #making error directory if error is present
                    os.mkdir(error_dir)
                error_row=[message.Mailbag_Message_ID,message.Original_Filename,message.Error]
                error_csv.append(error_row)
                filename=os.path.join(error_dir,str(message.Mailbag_Message_ID)+'.txt')
                with open(filename, 'w') as f:
                    f.write("\n".join(str(error) for error in message.StackTrace))


            #Generate derivatives
            for d in derivatives:
                d.do_task_per_message(message, self.args, mailbag_dir)

        # append any remaining csv portions < 100000
        csv_data.append(csv_portion)

        # Write CSV data to mailbag.csv
        log.debug("Writing mailbag.csv to " + str(mailbag_dir))
        if not self.args.dry_run:
            #Creating csv
            # checking if there are multiple portions in list or not
            if len(csv_data) == 1:
                filename = os.path.join(mailbag_dir, "mailbag.csv")
                with open(filename, 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(csv_data[0])
            else:
                portion_count = 0
                for portion in csv_data:
                    portion_count += 1
                    filename = os.path.join(mailbag_dir, "mailbag-" + str(portion_count) + ".csv")
                    with open(filename, 'w', encoding='UTF8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(portion)

        log.debug("Writing error.csv to " + str(error_dir))
        if not self.args.dry_run:
            if len(error_csv) > 1:
                filename = os.path.join(error_dir, "error.csv")
                with open(filename, 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(error_csv)




        if not self.args.dry_run:
            bag.save(manifests=True)

        return mail_account.messages()
