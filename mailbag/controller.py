from structlog import get_logger

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
        mail_account : EmailAccount = self.format(self.args.directory, self.args)

        derivatives = [d(mail_account) for d in self.derivatives_to_create]

        # do stuff you ought to do with per-account info here
        # mail_account.account_data()
        #for d in derivatives:
        #    d.do_task_per_account()

        #Create folder mailbag folder before writing mailbag.csv
        if os.path.isfile(self.args.directory):
            parent_dir = os.path.abspath(os.path.dirname(self.args.directory))
        else:
            parent_dir = os.path.abspath(self.args.directory)
        mailbag_dir = os.path.join(parent_dir, self.args.mailbag_name)
        log.debug("Creating mailbag at " + str(mailbag_dir))
        if not self.args.dry_run:
            os.mkdir(mailbag_dir)

        mailbag_message_id = 0

        for message in mail_account.messages():
            # do stuff you ought to do per message here

            # Generate mailbag_message_id
            mailbag_message_id += 1
            message.Mailbag_Message_ID = mailbag_message_id


            for d in derivatives:
                d.do_task_per_message(message, self.args, mailbag_dir)

        return mail_account.messages()
