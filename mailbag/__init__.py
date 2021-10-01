# __init__.py

# Version of the mailbag package
__version__ = "0.0.1"


from bagit import _make_parser, Bag
from gooey import Gooey

from mailbag.parser import EmailFormatParser

print(EmailFormatParser.registry)

bagit_parser = _make_parser()
bagit_parser.description = f"Mailbag ({bagit_parser.description})"
mailbagit_args = bagit_parser.add_argument_group("Mailbag arguments")
mailbagit_options = bagit_parser.add_argument_group("Mailbag options")

# add mailbag-specific required args here
mailbagit_args.add_argument("-i","--input", required=True, help="input type MBOX/PST/IMAP/EML/PDF/MSG", nargs=1)
mailbagit_args.add_argument("-d","--derivatives", required=True, help="derivative type(s) MBOX/PST/EML/PDF/WARC", nargs='+')

# add mailbag-specific optional args here
mailbagit_options.add_argument("--imap_host", help="the host for creating a mailbag from an IMAP connection", nargs=1)
mailbagit_options.add_argument("--imap_password", help="password for creating a mailbag from an IMAP connection", nargs=1)
mailbagit_options.add_argument("--exclude_folders", help="email folders to be excluded from the mailbag", nargs='+')
mailbagit_options.add_argument("--exclude_messages", help="a line-separated text file of Message-IDs to be excluded from a mailbag",nargs='+')
mailbagit_options.add_argument("-e", "--exclude_input", help="will also exclude email folders and/or messages from the input PST or MBOX file before including it in the mailbag", action='store_true')
mailbagit_options.add_argument("-l", "--crawl_links", help="will attempt to capture links in messages and include them in WARC output", action='store_true')
mailbagit_options.add_argument("-a", "--crawl-attached-links", help="will attempt to capture links attached to messages and include them in WARC output", action='store_true')
mailbagit_options.add_argument("-n", "--no-headers", help="will not include email headers in mailbag.csv", action='store_true')
mailbagit_options.add_argument("--pdf-css", help="Path to a CSS file to customize PDF derivatives.",nargs=1)
mailbagit_options.add_argument("-c", "--compress", help="Compress the mailbag as ZIP, TAR, or TAR.GZ",nargs='+')


def cli():
    bagit_parser.parse_args()
    # do the thing

@Gooey
def gui():
    bagit_parser.parse_args()
    #do the thing

class Mailbag:
    def __init__(self):
        print("Hello world!")
