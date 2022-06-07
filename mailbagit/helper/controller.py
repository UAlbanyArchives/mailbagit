import os, shutil, glob
import datetime
from time import time
import csv

import mailbagit.helper.common as common
import mailbagit.globals as globals

from structlog import get_logger

log = get_logger()


def progress(current, total, start_time, prefix="", suffix="", decimals=1, length=100, fill="█", print_End="\r"):
    """
    Call in a loop to create terminal progress bar

    Parameters:
        current (int): current progress
        total (int): total iterations
        start_time (float): start time
        prefix (String): prefix string
        suffix (String): suffix string
        decimals (int): positive number of decimals in percent complete
        length (int): character length of bar (Int)
        fill (String): bar fill character (Str)
        printEnd (String): end character (e.g. "\r", "\r\n")
    """

    time_spent = time() - start_time
    remaining_time = round(time_spent * (total / current - 1), 2)
    e = datetime.datetime.now()
    percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
    # filledLength = int(length * current // total)
    style = globals.style
    # bar = fill * filledLength + '-' * (length - filledLength)

    dt = f"{e.year}-{e.month:02d}-{e.day:02d} {e.hour:02d}:{e.minute:02d}.{e.second:02d}"
    message_type = f'[{style["cy"][0]}{prefix}{style["b"][1]}]'
    # deco_prefix = f'{style["b"][0]}{prefix}{style["b"][1]}'
    # statusBar = f'|{bar}| {percent}% [{current}MB out of {total}MB] {suffix}'
    status = f"{percent}% [{current} / {total} messages] {remaining_time}s remaining"

    print(f"\r{dt} {message_type} {status}", end=print_End)


def progressMessage(msg, print_End="\r"):
    """
    Shows a message as progress. Useful since it make take awhile to save large bags
    even after all messages have been processed.

    Parameters:
        msg (String): A message to show as progress
    """
    e = datetime.datetime.now()
    style = globals.style
    dt = f"{e.year}-{e.month:02d}-{e.day:02d} {e.hour:02d}:{e.minute:02d}.{e.second:02d}"
    message_type = f'[{style["cy"][0]}{"Progress "}{style["b"][1]}]'
    print(f"\r{dt} {message_type} {msg}", end=print_End)


def writeAttachmentsToDisk(dry_run, attachments_dir, message):
    """
    Takes an email message object and writes any attachments in the model
    to the attachments subdirectory according to the mailbag spec.
    Also creates attachments.csv according to the mailbag spec.

    Parameters:
        dry_run (Boolean): Option to do a test run without writing changes
        attachments_dir (Path): Path to the attachments subdirectory
        message (Email): A full email message object desribed in models.py
    """

    message_attachments_dir = os.path.join(attachments_dir, str(message.Mailbag_Message_ID))
    if not dry_run:
        os.mkdir(message_attachments_dir)

    # Set up attachments.csv
    attachments_csv = os.path.join(message_attachments_dir, "attachments.csv")
    attachments_headers = ["Original-Filename", "Mailbag-Filename", "MimeType", "Content-ID"]
    attachment_data = [attachments_headers]

    for i, attachment in enumerate(message.Attachments):
        if attachment.Name:
            # Need to handle filename conflicts with attachments.csv
            # The format parsers raise a warning about this
            if attachment.Name.lower() == "attachments.csv":
                writtenName = str(i) + os.path.splitext(attachment.Name)[1]
                desc = ""
                errors = common.handle_error(errors, None, desc, "warn")
            else:
                writtenName = attachment.Name
            attachment_row = [attachment.Name, writtenName, attachment.MimeType, attachment.Content_ID]
        else:
            # If there is no filename available, just use and integer
            # The format parsers raise an error about this
            writtenName = str(i)
            attachment_row = ["", writtenName, attachment.MimeType, attachment.Content_ID]
        attachment_data.append(attachment_row)

        log.debug("Saving Attachment:" + str(attachment.Name))
        log.debug("Type:" + str(attachment.MimeType))
        if not dry_run:
            attachment_path = os.path.join(message_attachments_dir, writtenName)
            f = open(attachment_path, "wb")
            f.write(attachment.File)
            f.close()

    # Write attachments.csv
    if not dry_run:
        with open(attachments_csv, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(attachment_data)
            csv_file.close()
