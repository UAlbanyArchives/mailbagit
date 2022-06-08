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
        input_string = input(query + " (Yes or No): ")
        allow_exit(input_string)
        if not input_string.lower().strip() in input_options:
            log.error("Invalid input. Must be one of: " + ", ".join(input_options))
        elif input_string.lower().strip() == "y" or input_string.lower().strip() == "yes":
            yes = True
    if yes:
        return True
    else:
        return False


def prompts(input_types, derivative_types):

    print('Mailbagit packages email export formats into a "mailbag".')
    """
    input_format = ""
    while not input_format.lower() in input_types:
    	input_format = input("Enter the file format you wish to package (" + ", ".join(input_types) + "): ")
    	allow_exit(input_format)
    	if not input_format.lower() in input_types:
    		log.error("Invalid format. Must be one of: " + ", ".join(input_types) + ".")
    
    path = ""
    pathValid = False
    while pathValid == False:
    	path = input("Enter a path to a " + input_format.upper() + " file or a directory containing " + input_format.upper() + " files: ")
    	allow_exit(path)
    	if os.path.isfile(path):
    		if path.lower().endswith("." + input_format.lower()):
    			pathValid = True
    		else:
    			log.error("File " + path + " is not a " + input_format.upper() + " file.")
    	elif os.path.isdir(path):
    		pathValid = True
    	else:
    		log.error("Must be a valid path to a file or directory.")
    """
    path = "..\\sampleData\\attachments\\single"
    input_format = "msg"

    derivatives_formats = ["invalid"]
    while not all(item in derivative_types for item in derivatives_formats):
        derivatives_input = input("Enter the derivatives formats to create separated by spaces (" + ", ".join(derivative_types) + "): ")
        allow_exit(derivatives_input)
        derivatives_formats = derivatives_input.split(" ")
        if not all(item in derivative_types for item in derivatives_formats):
            log.error("Invalid format(s). Must be included in: " + ", ".join(derivative_types) + ".")

    mailbag_name = "test123"
    """
    while len(mailbag_name) < 1 or os.path.isdir(os.path.join(path, mailbag_name)):
    	mailbag_name = input("Enter a name for the mailbag: ")
    	allow_exit(mailbag_name)
    	if len(mailbag_name) < 1:
    		log.error("Invalid path")
    	elif os.path.isdir(os.path.join(path, mailbag_name)):
    		log.error("A directory already exists at " + os.path.join(path, mailbag_name))
    """

    input_args = [sys.argv[0], path, "-i", input_format, "-m", mailbag_name, "-d"]
    input_args.extend(derivatives_formats)

    if yes_no("Would you like to try a dry run?"):
        input_args.append("-r")

    if yes_no("Would you like more options?"):

        if os.path.isdir(path):
            if yes_no("Would you like to include companion files (such as metadata files) that are present in the provided directory?"):
                input_args.append("-f")

    sys.argv = input_args
