import os
import sys
import pyreadline3
from structlog import get_logger

log = get_logger()


def allow_exit(input_string):
    if input_string.lower() == "exit":
        sys.exit()


def yes_no(query):
    input_string = ""
    input_options = ["yes", "y", "no", "n"]
    yes = False
    while not input_string.lower().strip() in input_options:
        input_string = input(query + " (" + ", ".join(input_options) + "): ")
        allow_exit(input_string)
        if not input_string.lower().strip() in input_options:
            log.error(f"Invalid input. Must be one of: {', '.join(input_options)}")
        elif input_string.lower().strip() == "y" or input_string.lower().strip() == "yes":
            yes = True
    if yes:
        return True
    else:
        return False


def in_options(query, options):
    input_string = ""
    while not input_string.lower() in options:
        input_string = input(f"{query} ({', '.join(options)}): ")
        allow_exit(input_string)
        if not input_string.lower() in options:
            log.error(f"Invalid input. Must be one of: {', '.join(options)}")
    return input_string


def prompts(input_types, derivative_types, hashes, metadata_fields):

    print('Mailbagit packages email export formats into a "mailbag".')

    # Which input format?
    input_format = in_options("Enter the file format you wish to package", input_types)

    # Path to files or directory
    path = ""
    pathValid = False
    while pathValid == False:
        path = input(f"Enter a path to a {input_format.upper()} file or a directory containing {input_format.upper()} files: ")
        allow_exit(path)
        if os.path.isfile(path):
            if path.lower().endswith("." + input_format.lower()):
                pathValid = True
            else:
                log.error(f"File {path} is not a {input_format.upper()} file.")
        elif os.path.isdir(path):
            pathValid = True
        else:
            log.error("Must be a valid path to a file or directory.")

    # What derivatives to create?
    # Don't allow same derivatives as input format
    if input_format in derivative_types:
        derivative_types.remove("eml")
    derivatives_formats = ["invalid"]  # Needs to start invalid because the loop ends when the values are valid.
    while not all(item in derivative_types for item in derivatives_formats):
        derivatives_input = input("Enter the derivatives formats to create separated by spaces (" + ", ".join(derivative_types) + "): ")
        allow_exit(derivatives_input)
        derivatives_formats = derivatives_input.split(" ")
        if not all(item in derivative_types for item in derivatives_formats):
            log.error(f"Invalid format(s). Must be included in: {', '.join(derivative_types)}.")

    # mailbag name
    mailbag_name = ""
    while len(mailbag_name) < 1 or os.path.isdir(os.path.join(path, mailbag_name)):
        mailbag_name = input("Enter a name for the mailbag: ")
        allow_exit(mailbag_name)
        if len(mailbag_name) < 1:
            log.error("Invalid path")
        elif os.path.isdir(os.path.join(path, mailbag_name)):
            log.error("A directory already exists at " + os.path.join(path, mailbag_name))

    # Basic setup basic args
    input_args = [sys.argv[0], path, "-i", input_format, "-m", mailbag_name, "-d"]
    input_args.extend(derivatives_formats)

    # dry run?
    if yes_no("Would you like to try a dry run?"):
        input_args.append("-r")

    # more options?
    if yes_no("Would you like more options?"):

        # Include companion files?
        if os.path.isdir(path):
            if yes_no("Would you like to include companion files (such as metadata files) that are present in the provided directory?"):
                input_args.append("-f")

        # Compress?
        input_format = in_options("Would you like to compress the mailbag?", ["no", "n", "zip", "tar", "tar.gz"])
        if not input_format == "no" and not input_format == "n":
            input_args.extend(["-c", input_format])

        # Custom CSS?
        # Only ask for HTML or PDF derivatives
        if "html" in derivatives_formats or any("pdf" in formats for formats in derivatives_formats):
            css = ""
            cssValid = False
            while cssValid == False:
                css = input("Would you like to apply custom CSS to HTML and PDF derivatives? ({path}, no, n): ")
                allow_exit(css)
                if css.lower().strip() == "no" or css.lower().strip() == "n":
                    cssValid = True
                elif os.path.isfile(css) and css.lower().endswith(".css"):
                    input_args.extend(["--css", css])
                    cssValid = True
                else:
                    log.error(f"{css} is not a path to a valid CSS file.")

        # Customize checksums?
        if yes_no("Mailbagit uses sha256 and sha512 by default. Would you like to customize the checksums used?"):
            custom_hashes = ["invalid"]  # Needs to start invalid because the loop ends when the values are valid.
            while not all(item in hashes for item in custom_hashes):
                hashes_input = input("Enter the derivatives formats to create separated by spaces (" + ", ".join(hashes) + "): ")
                allow_exit(hashes_input)
                custom_hashes = hashes_input.split(" ")
                if not all(item in hashes for item in custom_hashes):
                    log.error(f"Invalid checksums(s). Must be included in: ({', '.join(hashes)}).")
            for custom_hash in custom_hashes:
                input_args.append("--" + custom_hash)

        # Custom metadata?
        if yes_no("Do you want to add custom metadata in bag-info.txt?"):
            print("Optional Metadata Fields:")
            print("\t" + "\n\t".join(metadata_fields))
            custom_metadata = {}
            metadata_done = False
            while metadata_done == False:
                metadata_input = input('Enter a field and value separated by colon (:), or enter "done" when complete: ')
                allow_exit(metadata_input)
                if metadata_input.lower().strip() == "done":
                    metadata_done = True
                elif len(metadata_input) < 1 or not ":" in metadata_input:
                    log.error(f'Invalid input. Must be a field and value separated by a colon. e.g. "capture-agent: Microsoft Outlook"')
                else:
                    custom_key, custom_value = metadata_input.split(":", 1)
                    if not custom_key in metadata_fields:
                        log.error(f"Invalid field \"{custom_key}\". Must be included in: ({', '.join(metadata_fields)}).")
                    else:
                        print(f'--> Adding "{custom_key.strip()}: {custom_value.strip()}" to bag-info.txt.')
                        custom_metadata[custom_key.strip()] = custom_value.strip()
            for field in custom_metadata.keys():
                input_args.extend(["--" + field, custom_metadata[field]])

    log.debug("Guided arguments:", args=input_args)
    # Replace args with args from guided prompts
    sys.argv = input_args
