from structlog import get_logger

from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar

log = get_logger()


class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args, formats):
        self.args = args
    
    @property
    def format_map(self):
        return EmailAccount.registry

    def read(self):

        if len(self.args.directory) > 1:
            # checks that mailbag was only given one directory as input. 
            # bagit-python loops through all directory args, and we may have to 
            # handle multiple inputs at some point but for now just raise an error.
            log.error("Mailbag currently only reads one input source.")
            raise ValueError("Mailbag currently only reads one input source.")
        else:
            format = self.format_map[self.args.input](self.args.directory[0])            
            messages = format.messages()
        
        for m in messages:
            print(m.to_struct())
