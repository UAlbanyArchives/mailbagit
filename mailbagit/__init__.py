# __init__.py

# Version of the mailbagit package
__version__ = "0.7.4"

import os
from pathlib import Path
from bagit import _make_parser, Bag, BagHeaderAction, DEFAULT_CHECKSUMS
import importlib
from mailbagit.loggerx import setup_logging, get_logger
from argparse import ArgumentParser, FileType
from mailbagit.email_account import EmailAccount, import_formats
from mailbagit.derivative import Derivative, import_derivatives
from mailbagit.controller import Controller
from mailbagit.guided import prompts
import mailbagit.loggerx
import mailbagit.globals

globals.init()

if importlib.util.find_spec("gooey"):
    gooeyCheck = True
    from gooey import Gooey, GooeyParser
else:
    gooeyCheck = False

plugin_basedir = os.environ.get("MAILBAGIT_PLUGIN_DIR", None)

# Formats and derivatives are loaded from:
#   1. formats/derivatives directories inside the package (built-in)
#   2. .mailbagit/{formats,derivatives} in user home directory
#   3. {formats,derivatives} subdirectories in plugin dir set in environment variable
plugin_dirs = {"formats": [], "derivatives": []}
for plugin_type, dirs in plugin_dirs.items():
    dirs.append(Path(f"~/.mailbagit/{plugin_type}").expanduser())
    if plugin_basedir:
        dirs.append((Path(plugin_basedir) / plugin_type).expanduser())

import_formats(plugin_dirs["formats"])
import_derivatives(plugin_dirs["derivatives"])

bagit_parser = _make_parser()
if gooeyCheck:
    mailbag_parser = GooeyParser(description="Mailbagit")
else:
    mailbag_parser = ArgumentParser(description="Mailbagit")
mailbag_parser.set_defaults(bag_info={})
mailbagit_args = mailbag_parser.add_argument_group("Mailbagit arguments")
mailbagit_options = mailbag_parser.add_argument_group("Mailbagit options")
mailbagit_metadata = mailbag_parser.add_argument_group("Optional Mailbag Metadata")

# Get possible hashes and metadata fields from bagit_parser for guided input
hashes = []
metadata_fields = []

# Load relevant args from bagit_parser to mailbag_parser
# This is necessary as mailbagit does not support --validate, --fast, or --completeness-only
# Checksum args also do not action="store_true" so they don't display as checkboxes with Gooey
# Excluding log and quiet for not since we're not handling these yet
exclude_args = ["directory", "help", "validate", "fast", "completeness_only", "quiet"]
for arg_group in bagit_parser._action_groups:
    # print(arg_group.__dict__["title"].title())
    group = mailbag_parser.add_argument_group(arg_group.__dict__["title"].title())
    group.description = arg_group.__dict__["description"]
    for i, action in enumerate(arg_group._actions):
        if action.container == arg_group and not action.dest in exclude_args:
            # Get possible hashes from bagit_parser for guided input
            if action.dest == "checksums":
                hashes.append(action.option_strings[0][2:])
            if action.nargs == 0:
                # checksum options
                if gooeyCheck:
                    group.add_argument(
                        action.option_strings[0],
                        required=action.required,
                        default=action.default,
                        help=action.help,
                        dest=action.dest,
                        const=action.const,
                        action="append_const",
                        widget="BlockCheckbox",
                    )
                else:
                    group.add_argument(
                        action.option_strings[0],
                        required=action.required,
                        default=action.default,
                        help=action.help,
                        dest=action.dest,
                        const=action.const,
                        action="append_const",
                    )
            else:
                if arg_group.__dict__["title"].lower() == "optional bag metadata":
                    # bag_size is automatically set and cannot be overridden
                    if action.dest != "bag_size":
                        metadata_fields.append(action.dest.replace("_", "-"))
                        group.add_argument(
                            action.option_strings[0],
                            required=action.required,
                            default=action.default,
                            help=action.help,
                            type=str,
                            dest=action.dest.replace("_", "-"),
                            action=BagHeaderAction,
                            nargs=action.nargs,
                        )
                elif action.dest.lower() == "processes":
                    group.add_argument(
                        action.option_strings[0],
                        required=action.required,
                        default=action.default,
                        type=int,
                        help=action.help,
                        choices=action.choices,
                        dest=action.dest,
                        nargs=action.nargs,
                    )
                else:
                    group.add_argument(
                        action.option_strings[0],
                        required=action.required,
                        default=action.default,
                        help=action.help,
                        choices=action.choices,
                        dest=action.dest,
                        nargs=action.nargs,
                    )
    # append json stdout option to optional args from bagit parser
    if arg_group.__dict__["title"].lower() == "optional arguments":
        group.add_argument("-j", "--log-json", help="Format logs as JSON", default=False, action="store_true")


input_types = list(key for key in EmailAccount.registry.keys() if key != "example")
derivative_types = list(key for key in Derivative.registry.keys() if key != "example")

# Path arg to override bagit directory arg
mailbagit_args.add_argument(
    "path",
    nargs=1,
    # widget="DirChooser",
    help=("A path to email to be packaged into a mailbag. This can be a single file or a directory containing a number of email exports."),
)


# add mailbagit-specific required args here
mailbagit_args.add_argument(
    "-m",
    "--mailbag",
    required=True,
    help="A new directory for the mailbag, such as '/path/to/my_mailbag', or just 'my_mailbag' to use the same location as the source email.",
    nargs=None,
)
mailbagit_args.add_argument(
    "-i", "--input", required=True, help=f"The email export format to be packaged.", choices=input_types, type=str.lower, nargs=None
)

if gooeyCheck:
    mailbagit_args.add_argument(
        "-d",
        "--derivatives",
        choices=derivative_types,
        type=str.lower,
        required=False,
        help=f"types of derivative formats to create during packaging",
        nargs="+",
        widget="Listbox",
    )
else:
    mailbagit_args.add_argument(
        "-d",
        "--derivatives",
        choices=derivative_types,
        type=str.lower,
        required=False,
        help=f"types of derivative formats to create during packaging",
        nargs="+",
    )

# add mailbagit-specific optional args here
mailbagit_options.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
mailbagit_options.add_argument("--css", help="Path to a CSS file to customize PDF derivatives.", nargs=None)
mailbagit_options.add_argument(
    "-c", "--compress", help="Compress the mailbag as ZIP, TAR, or TAR.GZ.", nargs=None, choices=["tar", "zip", "tar.gz"]
)
mailbagit_options.add_argument(
    "-r", "--dry-run", help="A dry run performs a trial run with no changes made.", default=False, action="store_true"
)
mailbagit_options.add_argument(
    "-k", "--keep", help="Leaves source email as-is and makes a copy into a mailbag.", default=False, action="store_true"
)
mailbagit_options.add_argument(
    "-l", "--external-links", help="Crawl and add external <a> links to WARC derivatives", default=False, action="store_true"
)
mailbagit_options.add_argument(
    "-f",
    "--companion-files",
    help="Will copy all files in the path provided to mailbagit in to a mailbag regardless of extention.",
    default=False,
    action="store_true",
)

# Yet-to-be-implemented:
"""
mailbagit_options.add_argument("--imap_host", help="the host for creating a mailbag from an IMAP connection", nargs=None)
mailbagit_options.add_argument("--imap_password", help="password for creating a mailbag from an IMAP connection", nargs=None)
mailbagit_options.add_argument("--exclude_folders", help="email folders to be excluded from the mailbag", nargs="+")
mailbagit_options.add_argument(
    "--exclude_messages", help="a line-separated text file of Message-IDs to be excluded from a mailbag", nargs="+"
)
mailbagit_options.add_argument(
    "-e",
    "--exclude_input",
    help="will also exclude email folders and/or messages from the input PST or MBOX file before including it in the mailbag",
    action="store_true",
)
mailbagit_options.add_argument(
    "-l", "--crawl_links", help="will attempt to capture links in messages and include them in WARC output", action="store_true"
)
mailbagit_options.add_argument(
    "-a",
    "--crawl-attached-links",
    help="will attempt to capture links attached to messages and include them in WARC output",
    action="store_true",
)
mailbagit_options.add_argument("-n", "--no-headers", help="will not include email headers in mailbag.csv", action="store_true")
"""

# Optional user-supplied mailbag metadata
mailbagit_metadata.add_argument(
    "--capture-date",
    help="Timestamp denoting when the email included in a mailbag was originally captured.",
)
mailbagit_metadata.add_argument(
    "--capture-agent",
    help="A string field describing the agent used to capture the email included in a mailbag.",
)
mailbagit_metadata.add_argument(
    "--capture-agent-version",
    help="A string field describing the version of the agent used to capture the email included in a mailbag.",
)
# Prepend user-supplied mailbag metadata fields to guided input options
metadata_fields.insert(0, "capture-agent-version")
metadata_fields.insert(0, "capture-agent")
metadata_fields.insert(0, "capture-date")


def cli():
    """hook for CLI-only mailbagit invocation"""
    args = mailbag_parser.parse_args()
    main(args)


def guided():
    """hook for Guided CLI mailbagit invocation"""
    prompts(input_types, derivative_types, hashes, metadata_fields)
    args = mailbag_parser.parse_args()
    main(args)
    input(f"Mailbag finished packaging at { args.path }. Press any key to finish.")


if gooeyCheck:

    @Gooey(richtext_controls=True)
    def gui():
        """hook for GUI mailbagit invocation"""
        args = mailbag_parser.parse_args()
        main(args)


def main(args):
    if hasattr(args, "log_json"):
        setup_logging(stream_json=args.log_json, filename=args.log)
    else:
        setup_logging(filename=args.log)
    args.input = args.input.lower()

    if not os.path.exists(args.path[0]):
        error_msg = "Invalid path, does not exist as a file or directory."
        mailbag_parser.error((error_msg))

    if os.path.isdir(args.mailbag):
        error_msg = "Invalid mailbag. Directory must not already exist."
        mailbag_parser.error((error_msg))
    elif os.path.isfile(args.mailbag):
        error_msg = "Invalid mailbag. Must be a new directory that does not already exist."
        mailbag_parser.error((error_msg))

    if args.input in args.derivatives:
        error_msg = "Invalid derivatives, mailbagit does not support the source format as a derivative."
        mailbag_parser.error((error_msg))

    # Check for multiple pdf derivatives, like both pdf and pdf-chrome
    if ["pdf" in x for x in args.derivatives].count(True) > 1:
        error_msg = "Invalid derivatives, mailbagit can only use one module to make PDF derivatives"
        mailbag_parser.error((error_msg))

    if args.processes < 1:
        error_msg = "processes must be valid integer > 0"
        mailbag_parser.error((error_msg))

    # Raise and error and exit when given multiple inputs
    if len(args.path) > 1:
        error_msg = (
            "Multiple input paths provided. Mailbagit only supports packaging single input paths. "
            "You may want to try providing a directory of email or running the command multiple "
            "times to create multiple mailbags."
        )
        mailbag_parser.error((error_msg))

    args.path = args.path[0]
    c = Controller(args)
    return c.generate_mailbag()
