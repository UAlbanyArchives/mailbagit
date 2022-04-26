# __init__.py

# Version of the mailbag package
__version__ = "0.0.1"

import os
from pathlib import Path
from bagit import _make_parser, Bag
from gooey import Gooey
from structlog import get_logger
from argparse import ArgumentParser
from mailbag.email_account import EmailAccount, import_formats
from mailbag.derivative import Derivative, import_derivatives
from mailbag.controller import Controller
import mailbag.loggerx

loggerx.configure()
log = get_logger()

plugin_basedir = os.environ.get("MAILBAG_PLUGIN_DIR", None)

# Formats and derivatives are loaded from:
#   1. formats/derivatives directories inside the package (built-in)
#   2. .mailbag/{formats,dirivatives} in user home directory
#   3. {formats,dirivatives} subdirectories in plugin dir set in environment variable
plugin_dirs = {"formats": [], "derivatives": []}
for plugin_type, dirs in plugin_dirs.items():
    dirs.append(Path(f"~/.mailbag/{plugin_type}").expanduser())
    if plugin_basedir:
        dirs.append((Path(plugin_basedir) / plugin_type).expanduser())

import_formats(plugin_dirs["formats"])
import_derivatives(plugin_dirs["derivatives"])

log.debug("EmailAccount:", Registry=EmailAccount.registry)
log.debug("Derivative:", Registry=Derivative.registry)

bagit_parser = _make_parser()
mailbag_parser = ArgumentParser(description="Mailbag")
print(dir(bagit_parser))
# bagit_parser.description = f"Mailbag ({bagit_parser.description})"
mailbagit_args = mailbag_parser.add_argument_group("Mailbag arguments")
mailbagit_options = mailbag_parser.add_argument_group("Mailbag options")
mailbagit_metadata = mailbag_parser.add_argument_group("Optional Mailbag Metadata")

count = 0
for arg_group in bagit_parser._action_groups:
    count += 1
    # print (type(arg_group))
    # print (dir(arg_group))
    print(arg_group.__dict__["title"])
    group = mailbag_parser.add_argument_group(arg_group.__dict__["title"])
    group.description = arg_group.__dict__["description"]
    # group.add_argument("-" + str(count), "--input" + str(count), required=True, help=f"type of mailbox to be bagged", nargs=None)
    for action in arg_group._actions:
        if action.dest == "help":
            pass
        else:
            if action.container == arg_group:
                # print (action)
                # print (dir(action))
                # print (action.dest)
                # print (action.required)
                # print (action.help)
                # print (action.choices)
                # print (action.nargs)
                if len(action.option_strings) > 0:
                    if action.nargs == 0:
                        group.add_argument(
                            action.option_strings[0],
                            required=action.required,
                            default=action.default,
                            help=action.help,
                            action="store_true",
                        )
                    else:
                        group.add_argument(
                            action.option_strings[0],
                            required=action.required,
                            default=action.default,
                            help=action.help,
                            choices=action.choices,
                            nargs=action.nargs,
                        )

input_types = list(EmailAccount.registry.keys())
derivative_types = list(Derivative.registry.keys())

# add mailbag-specific required args here
mailbagit_args.add_argument(
    "-i", "--input", required=True, help=f"type of mailbox to be bagged", choices=input_types, type=str.lower, nargs=None
)

# add mailbag-specific optional args here
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
mailbagit_options.add_argument("--css", help="Path to a CSS file to customize PDF derivatives.", nargs=None)
mailbagit_options.add_argument(
    "-c", "--compress", help="Compress the mailbag as ZIP, TAR, or TAR.GZ", nargs=None, choices=["tar", "zip", "tar.gz"]
)
mailbagit_options.add_argument("-r", "--dry_run", help="Dry run", default=False, action="store_true")

# Optional user-supplied mailbag metadata
mailbagit_metadata.add_argument(
    "--capture-date", help="Timestamp denoting when the email included in a mailbag was originally captured.", nargs=None
)
mailbagit_metadata.add_argument(
    "--capture-agent", help="A string field describing the agent used to capture the email included in a mailbag.", nargs=None
)
mailbagit_metadata.add_argument(
    "--capture-agent-version",
    help="A string field describing the version of the agent used to capture the email included in a mailbag.",
    nargs=None,
)


def cli():
    """hook for CLI-only mailbag invocation"""
    mailbagit_args.add_argument(
        "-d",
        "--derivatives",
        choices=derivative_types,
        type=str.lower,
        required=False,
        help=f"types of derivatives to create before bagging",
        nargs="+",
    )
    mailbagit_args.add_argument("-m", "--mailbag_name", required=True, help="A directory name for the mailbag root directory.", nargs=None)
    main()


@Gooey
def gui():
    """hook for GUI mailbag invocation"""
    mailbagit_args.add_argument(
        "-d",
        "--derivatives",
        type=str.lower,
        required=False,
        help=f"types of derivatives to create before bagging separated by spaces. Such as 'pdf warc'",
        nargs=None,
    )
    mailbagit_args.add_argument("-m", "--mailbag_name", required=True, help="A directory name for the mailbag root directory.", nargs=None)
    main()


def main():
    args = mailbag_parser.parse_args()
    args.input = args.input.lower()
    if args.input not in EmailAccount.registry.keys():
        log.error("No parser found")
        exit()

    if isinstance(args.derivatives, str):
        args.derivatives = args.derivatives.split(" ")
        if not all(elem in derivative_types for elem in args.derivatives):
            error_msg = 'Invalid derivatives, choose from: "' + '", "'.join(derivative_types) + '"'
            log.error(error_msg)
            raise Exception(error_msg)

    log.debug("Arguments:", args=args)

    # Raise and error and exit when given multiple inputs
    if len(args.directory) > 1:
        log.error(
            "Multiple input paths provided. Mailbagit only supports single input paths. \
            You may want to try providing a directory of email or running the command multiple \
            times to create multiple mailbags."
        )
        exit()
    else:
        args.directory = args.directory[0]
        c = Controller(args)
        return c.generate_mailbag()
