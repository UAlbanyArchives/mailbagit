from structlog import get_logger

from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar

log = get_logger()


class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args):
        self.args = args
    
    @property
    def format_map(self):
        return EmailAccount.registry

    def read(self,input,directory):
        
        path = directory[0]
        format = self.format_map[input]
        
        if len(directory) > 1:
            # checks that mailbag was only given one directory as input. 
            # bagit-python loops through all directory args, and we may have to 
            # handle multiple inputs at some point but for now just raise an error.
            log.error("Mailbag currently only reads one input source.")
            raise ValueError("Mailbag currently only reads one input source.")
        else:
            self.reader(format,path)

    
    def reader(self,format,path):
        data = format(path)
        messages = data.messages()

        return messages
