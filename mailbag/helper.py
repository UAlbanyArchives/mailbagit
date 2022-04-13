import base64
import urllib.parse
from pathlib import Path
import os, shutil, glob

import bs4
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

def relativePath(mainPath, file):
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
        relPath = str(fullFilePath.relative_to(fullPath))
        if relPath == ".":
            return ""
        else:
            return relPath

def messagePath(headers):
        """
        Tries to read any email folder arragement from headers
        Useful for getting the path of messages within an email account
            
        Parameters:
            headers (email.message.Message): Can be used as a dict of email headers
            
        Returns:
            String: messagePath (must at least return an empty string)
        """

        if headers["X-Folder"]:
            messagePath = headers["X-Folder"].replace("\\", "/")
        else:
            messagePath = ""
        return messagePath
        
def moveWithDirectoryStructure(dry_run, mainPath, mailbag_name, input, file):
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
        relPath = fullFilePath.relative_to(fullPath).parents[0]
        filename = fullFilePath.name
        folder_new = os.path.join(fullPath, mailbag_name,'data', input)
        
        file_new_path = os.path.join(folder_new, relPath, filename)

        log.debug('Moving: ' + str(fullFilePath) + ' to: ' + str(file_new_path) + ' SubFolder: ' + str(relPath))
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


def htmlformatting(message,external_css):

    # check to see which body to use
    body = False
    encoding=False
    if message.HTML_Body:
        body = message.HTML_Body
        encoding = message.HTML_Encoding


    elif message.Text_Body:
        #  converting text body to html body
        body = "<html>" + "<body>" + message.Text_Body + "</body></html>"
        encoding = message.Text_Encoding

    else:
        log.debug("Unable to create PDF, no body found for " + str(message.Mailbag_Message_ID))
        return body

    if body:
        table = "<table>"
        headerFields = []
        # Getting all the required attributes of message except error and body
        for attribute in message:
            if (attribute[0] not in (
            "Error", "Text_Body", "Text_Bytes", "HTML_Body", "HTML_Bytes", "Message", "Headers", "AttachmentFiles")):
                headerFields.append(attribute[0])
        # Getting the values of the attrbutes and appending to HTML string
        for headerField in headerFields:
            if not getattr(message, headerField) is None:
                table += "<tr>"
                table += "<td>" + str(headerField) + "</td>"
                table += "<td>" + str(getattr(message, headerField)) + "</td>"
                table += "</tr>"
        table += "</table>"

        # add headers table to html
        if message.HTML_Body and "<body" in body.lower():
            body_position = body.lower().index("<body")
            table_position = body_position + body[body_position:].index(">") + 1
            html_content = body[:table_position] + table + body[table_position:]
        else:
            # fallback to just prepending the table
            html_content = table+body

        # add encoding
        meta = "<meta charset=\"" + encoding + "\">"
        if message.HTML_Encoding and "<head" in html_content.lower():
            head_position = html_content.lower().index("<head")
            meta_position = head_position + html_content[head_position:].index(">") + 1
            html_encoded = html_content[:meta_position] + meta + html_content[meta_position:]
        else:
            # fallback to just prepending the tag
            html_encoded = meta + html_content



        #Formatting HTML with beautiful soup
        soup = bs4.BeautifulSoup(html_content, 'html.parser')

        #Handling line-breaks
        tag = soup.head
        if tag:
            # Create new tag for style
            style = soup.new_tag("style")
            style.string = "body{ white-space: pre;}"
            soup.head.insert(1, style)
        else:
            # create new head tag with style embedded
            head = soup.new_tag("head")
            soup.html.body.insert_before(head)
            # Create new tag for style
            style = soup.new_tag("style")
            style.string="body{ white-space: pre;}"
            soup.head.insert(1, style)

        #Embedding table styling
        tag = soup.table
        tag['border'] = 1
        tag['cellspacing'] = 10
        tag['cellpadding'] = 10
        tag['align'] = 'center'
        tag['style']="width:500px;"

        #Adding external_css
        if external_css:
            tag=soup.head
            if tag:
                # Create new tag for link
                link = soup.new_tag("link")
                link["rel"] = "stylesheet"
                link['href'] = external_css
                soup.head.insert(1, link)
            else:
                # create new head tag with style embedded
                head = soup.new_tag("head")
                soup.html.body.insert_before(head)
                #Create new tag for link
                link=soup.new_tag("link")
                link["rel"]="stylesheet"
                link['href']=external_css
                soup.head.insert(1,link)

        # Embedding Images
        tags = (tag for tag in soup.findAll('img') if tag.get('src') and tag.get('src').startswith('cid:'))
        data = None
        for tag in tags:
            # Iterate through the attachments until we get the right one.
            cid = tag['src'][4:]

            for i in range(message.AttachmentNum):
                if message.AttachmentNames[i] in cid:
                    data = message.AttachmentFiles[i]

            # If we found anything, inject it.
            if data:
                tag['src'] = (b'data:image;base64,' + base64.b64encode(data)).decode('utf-8')

        return soup.prettify()

