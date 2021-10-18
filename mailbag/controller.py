from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil


class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args):
        self.args = args
    
    @property
    def format_map(self):
        return EmailAccount.registry

    def read(self, input, directory):
        
        path = directory[0]
        format = self.format_map[input]
        
        if len(directory) > 1:
            # checks that mailbag was only given one directory as input. 
            # bagit-python loops through all directory args, and we may have to 
            # handle multiple inputs at some point but for now just raise an error.
            raise ValueError("Mailbag currently only reads one input source.")
        else:
            self.reader(format, path)
    
    def reader(self, format, path):
        data = format(path)
        messages = data.messages()

        return messages
    
    def organizeFileStructure(self, input, directory):
        """ Create new directories if needed then move files to corresponding directory """
        path = Path(directory[0])
        folder = path.parent
        folder_new = os.path.join(folder, input)
        print('Moving:', str(path), 'to:', folder_new)
        Path(folder_new).mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), folder_new)
