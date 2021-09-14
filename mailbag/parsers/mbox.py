from mailbag.parser import EmailFormatParser
import mailbox

class Mbox(EmailFormatParser):
    """Mbox - This concrete class parses mbox file format"""
    parser_name = 'mbox'

    def parse(self, *args, **kwargs):
        """Parses the mbox file
        
        Args:
            'file' (key) : The file path of mbox file
            
        Example:
            parse(file="/sample.mbox")
        """
        mbox_file = kwargs['file']
        print("Reading mails from :",mbox_file)        
        mbox = mailbox.mbox(mbox_file)
        
        for key in mbox.iterkeys():

            try:
                message = mbox[key]
            except mbox.errors.MessageParseError:
                continue

            __class__.allMails.append(vars(message))