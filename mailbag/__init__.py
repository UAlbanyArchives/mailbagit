# __init__.py

# Version of the mailbag package
__version__ = "0.0.1"

import os
from pathlib import Path
from bagit import _make_parser, Bag
from gooey import Gooey
from mailbag.email_account import EmailAccount, import_formats
from mailbag.controller import Controller

plugin_dir = os.environ.get('MAILBAG_PLUGIN_DIR', None)

# Formats are loaded from:
#   1. formats directory inside the package (built-in)
#   2. .mailbag/formats in user home directory
#   3. plugin dir set in environment variable
format_dirs = []
format_dirs.append(Path("~/.mailbag/formats").expanduser())
if plugin_dir:
    format_dirs.append((Path(plugin_dir) / 'formats').expanduser())

import_formats(format_dirs)
print(EmailAccount.registry)

bagit_parser = _make_parser()
bagit_parser.description = f"Mailbag ({bagit_parser.description})"
mailbagit_args = bagit_parser.add_argument_group("Mailbag arguments")
mailbagit_options = bagit_parser.add_argument_group("Mailbag options")

# add mailbag-specific required args here
mailbagit_args.add_argument("-i","--input", required=True, help="input type MBOX/PST/IMAP/EML/PDF/MSG", nargs=None)
mailbagit_args.add_argument("-d","--derivatives", required=True, help="derivative type(s) MBOX/PST/EML/PDF/WARC", nargs='+')

# add mailbag-specific optional args here
mailbagit_options.add_argument("--imap_host", help="the host for creating a mailbag from an IMAP connection", nargs=None)
mailbagit_options.add_argument("--imap_password", help="password for creating a mailbag from an IMAP connection", nargs=None)
mailbagit_options.add_argument("--exclude_folders", help="email folders to be excluded from the mailbag", nargs='+')
mailbagit_options.add_argument("--exclude_messages", help="a line-separated text file of Message-IDs to be excluded from a mailbag",nargs='+')
mailbagit_options.add_argument("-e", "--exclude_input", help="will also exclude email folders and/or messages from the input PST or MBOX file before including it in the mailbag", action='store_true')
mailbagit_options.add_argument("-l", "--crawl_links", help="will attempt to capture links in messages and include them in WARC output", action='store_true')
mailbagit_options.add_argument("-a", "--crawl-attached-links", help="will attempt to capture links attached to messages and include them in WARC output", action='store_true')
mailbagit_options.add_argument("-n", "--no-headers", help="will not include email headers in mailbag.csv", action='store_true')
mailbagit_options.add_argument("--pdf-css", help="Path to a CSS file to customize PDF derivatives.",nargs=None)
mailbagit_options.add_argument("-c", "--compress", help="Compress the mailbag as ZIP, TAR, or TAR.GZ",nargs=None)
mailbagit_options.add_argument("-r", "--dry_run", help="Dry run", default=False, action="store_true")
mailbagit_options.add_argument("-m", "--mailbag_name", help="Mailbag name", nargs=None)


def cli():
    args = bagit_parser.parse_args()
    print (args)
    return Mailbag(args)


@Gooey
def gui():
    bagit_parser.parse_args()
    # do the thing


class Mailbag:

    def __init__(self, args):
        
        if args.input in EmailAccount.registry.keys():
            print("Mailbag name", args.mailbag_name)
            c = Controller(args)

            c.read(args.input, args.directory)
            c.organizeFileStructure(args.dry_run, args.mailbag_name, args.input, args.directory)

        else:
            print ("no parser found")
