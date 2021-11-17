from pathlib import Path
import os, shutil, glob

def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        shutil.copy(oldPath, newPath)
    except IOError as e:
        print('Unable to move file. %s' % e)
        
def emailFolder(dry_run, mailbag_name, input, mainPath, file):
        """
        Create new directories if needed then move files to corresponding directory
            
        Parameters:
            dry_run (Boolean): 
            mailbag_name (String): Mailbag name 
            input (String): Mail type
            mainPath (String): Parent or provided directory path
            file (String): Email file path
            
        Returns:
            String: emailFolder
        """

        filename = Path(file).name
        folder_new = os.path.join(mainPath, mailbag_name, 'data', input)
        
        subFolders = file[len(mainPath):len(file) - len(filename) - 1]
        file_new_path = os.path.join(folder_new, subFolders, filename)

        print('Moving:', file, 'to:', file_new_path, 'SubFolder:', subFolders)
        if(not dry_run):
            moveFile(dry_run, file, file_new_path)

        return subFolders
    