from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil, glob
import mailbag.helper as helper


class Controller:
    """Controller - Main controller"""
    
    def __init__(self, args):
        self.args = args
    
    @property
    def format_map(self):
        return EmailAccount.registry

    def read(self, input, directory):
        
        format = self.format_map[input]
        
        for path in directory:
            self.reader(format, path)
    
    def reader(self, format, path):
        data = format(self.args.dry_run,self.args.mailbag_name, path)
        messages = data.messages()
        
        for message in messages:
            print(message.to_struct())
        return messages
