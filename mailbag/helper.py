import urllib.parse
from pathlib import Path
import os, shutil, glob
from structlog import get_logger

log = get_logger()

def moveFile(dry_run, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        log.debug("from: " + str(oldPath))
        log.debug("to: " + str(newPath))
        shutil.move(oldPath, newPath)
    except IOError as e:
        log.error('Unable to move file. %s' % e)

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
        folder_new = os.path.join(fullPath, mailbag_name,'data', input)
        
        file_new_path = os.path.join(folder_new, emailFolder, filename)

        log.debug('Moving: ' + str(fullFilePath) + ' to: ' + str(file_new_path) + ' SubFolder: ' + str(emailFolder))
        if(not dry_run):
            moveFile(dry_run, fullFilePath, file_new_path)
            # clean up old directory structure
            p = fullFilePath.parents[0]
            while p != p.root and p != fullPath:
                if not os.listdir(p):
                    log.debug('Cleaning: ' + str(p))
                    os.rmdir(p)
                    # dirty hack since rmdir is not synchronous on Windows
                    if os.name == "nt":
                        import time
                        time.sleep(0.01)
                p = p.parent

        return file_new_path

def saveAttachments(part):
    return (part.get_filename(),part.get_payload(decode=True))


def saveAttachmentOnDisk(dry_run,attachments_dir,message):
    
    if not dry_run:
        message_attachments_dir = os.path.join(attachments_dir,str(message.Mailbag_Message_ID))
        os.mkdir(message_attachments_dir)
    for i in range(message.AttachmentNum):
        log.debug('Saving Attachment:'+str(message.AttachmentNames[i]))
        if not dry_run:
            attachment_path = os.path.join(message_attachments_dir,message.AttachmentNames[i])
            f = open(attachment_path, "wb")
            f.write(message.AttachmentFiles[i])
            f.close()

def normalizePath(path):
    # this is not sufficent yet
    if os.name == "nt":
        specials = ["<", ">", ":", "\"", "/", "|", "?", "*"]
        special_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", \
        "COM", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
        new_path = []
        for name in os.path.normpath(path).split(os.sep):
            illegal = False
            for char in specials:
                if char in name:
                    illegal = True
            if illegal:
                new_path.append(urllib.parse.quote_plus(name))
            else:
                new_path.append(name)
        return os.path.join(*new_path)
    else:
        return path
