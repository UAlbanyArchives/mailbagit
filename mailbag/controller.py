from mailbag.email_account import EmailAccount
from dataclasses import dataclass, asdict, field, InitVar
from pathlib import Path
import os, shutil, glob


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
        data = format(path)
        messages = data.messages()

        return messages
    
    def moveFile(self, dry_run, oldPath, newPath):
        os.makedirs(os.path.dirname(newPath), exist_ok=True)
        try:
            shutil.copy(oldPath, newPath)
        except IOError as e:
            print('Unable to copy file. %s' % e)
            
    def organizeFileStructure(self, dry_run, mailbag_name, input, directory):
        """ Create new directories if needed then move files to corresponding directory """
        
        for mainPathStr in directory:
            mainPath = Path(mainPathStr)
            mainfolder = str(mainPath.parent)
            
            if(input in ['mbox', 'pst']):
                
                file_new_path = os.path.join(mainfolder, mailbag_name, 'data', input, mainPath.name)
                
                print('Moving:', mainPathStr, 'to:', str(file_new_path))
                if(not dry_run):
                    self.moveFile(dry_run, mainPathStr, file_new_path)
  
            else:
                # Move multiple files recursively  
                files = glob.glob(os.path.join(mainPathStr, "**", "*." + input), recursive=True)
                for file in files:
                    filename = Path(file).name
                    folder_new = os.path.join(mainPathStr, mailbag_name, 'data', input)
                    
                    subFolders = file[len(mainPathStr):len(file) - len(filename) - 1]
                    file_new_path = os.path.join(folder_new, subFolders, filename)
    
                    print('Moving:', file, 'to:', file_new_path, 'SubFolder:', subFolders)
                    if(not dry_run):
                        self.moveFile(dry_run, file, file_new_path)
        
