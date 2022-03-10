from pathlib import Path
import os, shutil, glob

# import glob, os
# import extract_msg

def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        print ("from: " + str(oldPath))
        print ("to: " + str(newPath))
        shutil.move(oldPath, newPath)
    except IOError as e:
        print('Unable to move file. %s' % e)

def emailFolder(mainPath, file):
        """
        Gets the relative path of an input file within the input directory structure
        Useful for getting the path of messages within an email account
            
        Parameters:
            mainPath (String): Parent or provided directory path
            file (String): Email file path
            
        Returns:
            String: emailFolder
        """

        fullPath = Path(mainPath).resolve()
        fullFilePath = Path(file).resolve()
        
        subFolders = str(fullFilePath.relative_to(fullPath).parents[0])
        return subFolders
        
def moveWithDirectoryStructure(dry_run, mainPath, mailbag_name, input, emailFolder, file):
        """
        Create new mailbag directory structure while maintaining the input data's directory structure.
        Useful for MBOX, EML, and MSG files.
            
        Parameters:
            dry_run (Boolean): 
            mainPath (String): Parent or provided directory path
            mailbag_name (String): Mailbag name 
            input (String): Mail type
            emailFolder (String): Path of the email export file relative to mainPath
            file (String): Email file path
            
        Returns:
            file_new_path (Path): The path where the file was moved
        """

        fullPath = Path(mainPath).resolve()
        fullFilePath = Path(file).resolve()
        filename = fullFilePath.name
        folder_new = os.path.join(fullPath, mailbag_name, 'data', input)
        
        file_new_path = os.path.join(folder_new, emailFolder, filename)

        print('Moving:', fullFilePath, 'to:', file_new_path, 'SubFolder:', emailFolder)
        if(not dry_run):
            moveFile(dry_run, fullFilePath, file_new_path)
            # clean up old directory structure
            p = fullFilePath.parents[0]
            while p != p.root and p != fullPath:
                if not os.listdir(p):
                    print ('Cleaning:', p)
                    os.rmdir(p)
                    # dirty hack since rmdir is not synchronous on Windows
                    if os.name == "nt":
                        import time
                        time.sleep(0.01)
                p = p.parent

        return file_new_path

def saveAttachments(part):
    return (part.get_filename(),part.get_payload(decode=True))
    