from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar

class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args):
        self.args = args
    
    @property
    def format_map(self):
        return EmailAccount.registry

    def read(self):

        if len(self.args.directory) > 1:
            # checks that mailbag was only given one directory as input. 
            # bagit-python loops through all directory args, and we may have to 
            # handle multiple inputs at some point but for now just raise an error.
            raise ValueError("Mailbag currently only reads one input source.")
        else:

            format = self.format_map[self.args.input](self.args.directory[0])            
            messages = format.messages()
        
        for m in messages:
            print(m.to_struct())
