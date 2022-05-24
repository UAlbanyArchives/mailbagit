import os
from bagit import _make_parser, Bag
from mailbagit.email_account import EmailAccount
from mailbagit.controller import Controller

bagit_parser = _make_parser()
bagit_parser.description = f"Mailbagit ({bagit_parser.description})"
args = bagit_parser.parse_args()
parsers = ["pst", "mbox", "msg", "eml"]

for parser in parsers:
    args.input = parser
    args.derivatives = ["html"]
    args.dry_run = True
    args.mailbag_name = "test_data"
    args.companion_files = False

    controller = Controller(args)

    mail_account: EmailAccount = controller.format(args.directory[0], args)
    count = 0
    for message in mail_account.messages():
        count += 1
        message.Mailbag_Message_ID = count
        message.dump()
