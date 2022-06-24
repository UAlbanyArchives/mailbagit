import argparse
import bagit

from structlog import get_logger
import csv
import mailbagit
from mailbagit.email_account import EmailAccount
from mailbagit.derivative import Derivative
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil, glob
import mailbagit.helper.controller as controller
import mailbagit.globals as globals
from time import time
import uuid
import datetime
import traceback

log = get_logger()


class Controller:
    """Controller - Main controller"""

    def __init__(self, args):
        self.args = args
        self.format = self.format_map[args.input]
        self.derivatives_to_create = [self.derivative_map[d] for d in args.derivatives]

        self.csv_headers = [
            "Error",
            "Mailbag-Message-ID",
            "Message-ID",
            "Original-File",
            "Message-Path",
            "Derivatives-Path",
            "Attachments",
            "Date",
            "From",
            "To",
            "Cc",
            "Bcc",
            "Subject",
            "Content-Type",
        ]

    @property
    def format_map(self):
        return EmailAccount.registry

    @property
    def derivative_map(self):
        return Derivative.registry

    def message_to_csv(self, message, csv_type="all"):
        """
        Builds a list used for CSV output lines for mailbag.csv and error reports

        Parameters:
            message (Email): Email model object

        Returns:
            list: line
        """
        error_field = []
        for error in message.Errors:
            if csv_type == "all" or csv_type == error.Level.lower():
                error_field.append(error.Description)
        line = [
            " ".join(error_field),
            message.Mailbag_Message_ID,
            message.Message_ID,
            message.Original_File,
            message.Message_Path,
            message.Derivatives_Path,
            str(len(message.Attachments)),
            message.Date,
            message.From,
            message.To,
            message.Cc,
            message.Bcc,
            message.Subject,
            message.Content_Type,
        ]

        return line

    def human_size(self, size, units=[" bytes", " KB", " MB", " GB", " TB", " PB", " EB"]):
        """Returns a human readable string representation of bytes"""
        # HT https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
        return str(size) + units[0] if size < 1024 else self.human_size(size >> 10, units[1:])

    def generate_mailbag(self):

        mail_account: EmailAccount = self.format(self.args.path, self.args)

        # Create folder mailbag folder before writing mailbag.csv
        if os.path.isfile(self.args.path):
            parent_dir = os.path.dirname(self.args.path)
        else:
            parent_dir = self.args.path
        mailbag_dir = os.path.join(parent_dir, self.args.mailbag_name)
        attachments_dir = os.path.join(str(mailbag_dir), "data", "attachments")
        error_dir = os.path.join(parent_dir, str(self.args.mailbag_name) + "_errors")
        warn_dir = os.path.join(parent_dir, str(self.args.mailbag_name) + "_warnings")

        log.debug("Creating mailbag at " + str(mailbag_dir))
        if not self.args.dry_run:
            os.mkdir(mailbag_dir)
            # Creating a bagit-python style bag
            bag = bagit.make_bag(mailbag_dir, self.args.bag_info, processes=self.args.processes, checksums=self.args.checksums)
            bag.info["Bag-Type"] = "Mailbag"
            bag.info["Mailbag-Specification-Version"] = "0.3"
            bag.info["Mailbag-Source"] = self.args.input.lower()
            bag.info["Original-Included"] = "True"
            bag.info["Mailbag-Agent"] = mailbagit.__name__
            bag.info["Mailbag-Agent-Version"] = mailbagit.__version__
            # Make sure now custom external-idenifier is in args
            if not "external-identifier" in set(key.lower() for key in self.args.bag_info.keys()):
                bag.info["External-Identifier"] = uuid.uuid4()
            # user-supplied mailbag metadata
            user_metadata = ["Capture-Date", "Capture-Agent", "Capture-Agent-Version"]
            for user_field in user_metadata:
                if getattr(self.args, user_field.lower().replace("-", "_")):
                    bag.info[user_field] = getattr(self.args, user_field.lower().replace("-", "_"))
            # source format metadata
            bag.info[self.args.input.upper() + "-Agent"] = mail_account.format_agent
            bag.info[self.args.input.upper() + "-Agent-Version"] = mail_account.format_agent_version

        # Instantiate derivatives
        derivatives = [d(mail_account, args=self.args, mailbag_dir=mailbag_dir) for d in self.derivatives_to_create]
        if not self.args.dry_run:
            # write derivatives metadata
            for d in derivatives:
                if len(d.derivative_agent) > 0:
                    bag.info[d.derivative_format.upper() + "-Agent"] = d.derivative_agent
                if len(d.derivative_agent_version) > 0:
                    bag.info[d.derivative_format.upper() + "-Agent-Version"] = d.derivative_agent_version

        # do stuff you ought to do with per-account info here
        # mail_account.account_data()
        # for d in derivatives:
        #    d.do_task_per_account()

        # Setting up mailbag.csv
        csv_data = []
        mailbag_message_id = 0
        csv_portion_count = 0
        csv_portion = [self.csv_headers]
        error_csv = [self.csv_headers]
        warn_csv = [self.csv_headers]

        companion_files = []
        if os.path.isfile(self.args.path):
            parent_dir = os.path.dirname(self.args.path)
            fileList = [self.args.path]
        else:
            parent_dir = self.args.path
            fileList = []
            for root, dirs, files in os.walk(self.args.path):
                for file in files:
                    mailbag_path = os.path.join(self.args.path, self.args.mailbag_name) + os.sep
                    fileRoot = root + os.sep
                    # don't count the newly-created mailbag
                    if not fileRoot.startswith(mailbag_path):
                        if file.lower().endswith("." + mail_account.format_name):
                            fileList.append(os.path.join(root, file))
                        elif self.args.companion_files:
                            companion_files.append(os.path.join(root, file))

        # Count total no. of messages and set start time
        mail_account.iteration_only = True
        total_messages = len(list(mail_account.messages(fileList)))
        mail_account.iteration_only = False
        start_time = time()

        for message in mail_account.messages(fileList):
            # do stuff you ought to do per message here

            print(message.Subject)

            # Move MSG to new mailbag directory structure
            # new_path = format.moveWithDirectoryStructure(self.args.dry_run, parent_dir, self.args.mailbag_name, mail_account.format_name, os.path.join(self.args.path, message.Original_File))

            # Generate mailbag_message_id
            mailbag_message_id += 1
            message.Mailbag_Message_ID = mailbag_message_id

            if len(message.Attachments) > 0:
                if not os.path.isdir(attachments_dir) and not self.args.dry_run:
                    os.mkdir(attachments_dir)
                controller.writeAttachmentsToDisk(self.args.dry_run, attachments_dir, message)

            # Setting up CSV data
            # checking if the count of messages exceed 100000 and creating a new portion if it exceeds
            if csv_portion_count > 100000:
                csv_data.append(csv_portion)
                csv_portion = [self.csv_headers]
                csv_portion.append(self.message_to_csv(message))
                csv_portion_count = 0
            # if count is less than 100000 , appending the messages in one list
            else:
                csv_portion.append(self.message_to_csv(message))
            csv_portion_count += 1

            # Generate derivatives
            for d in derivatives:
                message = d.do_task_per_message(message)

            # Error and Warning Reports
            if len(message.Errors) > 0:
                error_stack_trace = []
                warn_stack_trace = []
                for error in message.Errors:
                    if error.Level.lower() == "warn":
                        warn_stack_trace.append(error.StackTrace)
                    else:
                        error_stack_trace.append(error.StackTrace)

                # Write Error Report
                if len(error_stack_trace) > 0:
                    if not os.path.isdir(error_dir):
                        # making error directory if error is present
                        os.mkdir(error_dir)
                    error_csv.append(self.message_to_csv(message, "error"))
                    error_trace_file = os.path.join(error_dir, str(message.Mailbag_Message_ID) + ".txt")
                    with open(error_trace_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(error_stack_trace))
                        f.close()

                # Write Warning Report
                if len(warn_stack_trace) > 0:
                    if not os.path.isdir(warn_dir):
                        # making error directory if error is present
                        os.mkdir(warn_dir)
                    warn_csv.append(self.message_to_csv(message, "warn"))
                    warn_trace_file = os.path.join(warn_dir, str(message.Mailbag_Message_ID) + ".txt")
                    with open(warn_trace_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(warn_stack_trace))
                        f.close()

            # Show progress
            # If progress%(total_messages/100)==0 then show progress
            # This reduces progress update overhead to only 100 updates at max
            is_first = mailbag_message_id == 1
            is_last = mailbag_message_id == total_messages
            if total_messages / 100 < 1 or is_first or is_last or mailbag_message_id % int(total_messages / 100) == 0:
                print_End = "\n" if globals.log_level == "DEBUG" or is_last else "\r"
                controller.progress(
                    mailbag_message_id, total_messages, start_time, prefix="Progress ", suffix="Complete", print_End=print_End
                )

        # if self.companion_files:
        #    # Move all files into mailbag directory structure
        #    for companion_file in companion_files:
        #        new_path = format.moveWithDirectoryStructure(self.dry_run, self.path, self.mailbag_name, self.format_name, companion_file)

        # End thread and server for WARC derivatives
        for d in derivatives:
            if "warc.WarcDerivative" in str(type(d)):
                d.terminate()

        # append any remaining csv portions < 100000
        csv_data.append(csv_portion)

        # Write CSV data to mailbag.csv
        log.debug("Writing mailbag.csv to " + str(mailbag_dir))
        if not self.args.dry_run:
            # Creating csv
            # checking if there are multiple portions in list or not
            if len(csv_data) == 1:
                filename = os.path.join(mailbag_dir, "mailbag.csv")
                with open(filename, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(csv_data[0])
                    f.close()
            else:
                portion_count = 0
                for portion in csv_data:
                    portion_count += 1
                    filename = os.path.join(mailbag_dir, "mailbag-" + str(portion_count) + ".csv")
                    with open(filename, "w", encoding="utf-8", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(portion)
                        f.close()

        controller.progressMessage("Writing CSVs...")
        log.debug("Writing error.csv to " + str(error_dir))
        if len(error_csv) > 1:
            filename = os.path.join(error_dir, "error.csv")
            with open(filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(error_csv)
        log.debug("Writing warnings.csv to " + str(warn_dir))
        if len(warn_csv) > 1:
            filename = os.path.join(warn_dir, "warnings.csv")
            with open(filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(warn_csv)

        if not self.args.dry_run:
            bag_size = 0
            for root, dirs, files in os.walk(os.path.join(str(mailbag_dir), "data")):
                for file in files:
                    bag_size += os.stat(os.path.join(root, file)).st_size
            bag.info["Bag-Size"] = self.human_size(bag_size)

            now = datetime.datetime.now()
            bag.info["Bagging-Timestamp"] = now.strftime("%Y-%m-%dT%H:%M:%S")
            bag.info["Bagging-Date"] = now.strftime("%Y-%m-%d")
            controller.progressMessage("Generating manifests...")
            bag.save(manifests=True)

        if self.args.compress and not self.args.dry_run:
            controller.progressMessage("Compressing mailbag...")
            log.info("Compressing Mailbag")
            compressionFormats = {"tar": "tar", "zip": "zip", "tar.gz": "gztar"}
            shutil.make_archive(mailbag_dir, compressionFormats[self.args.compress], mailbag_dir)

            # Checking if the files with all the given extensions are present
            if os.path.isfile(mailbag_dir + "." + self.args.compress):
                # Deleting the mailbag if compressed files are present
                shutil.rmtree(mailbag_dir)

        controller.progressMessage("Finished packaging mailbag.", print_End="\n")

        # return mail_account.messages()
        return mail_account
