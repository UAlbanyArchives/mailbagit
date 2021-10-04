from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar

class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args, formats):
        self.args = args
    
    @property
    def format_map(self):
        return EmailAccount.registry

    def read(self):

        format = self.format_map[self.args.input](self.args)            
        messages = format.messages()
        
        for m in messages:
            print(m.to_struct())
