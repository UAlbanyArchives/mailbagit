from structlog import get_logger
import email
import mailbox
import sys, os, string, re

log = get_logger()


from mailbag.derivative import Derivative
class MboxDerivative(Derivative):
    derivative_name = 'mbox2'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self,mail_account,args):
        new_path = os.path.join(args.directory, args.mailbag_name,"derivative.mbox")
        mbox = mailbox.mbox(new_path)
        mbox.lock()
        #appending all the message attributes of str type but getting error
        #HeaderParseError("header value appears to contain " email.errors.HeaderParseError: header value appears to contain an embedded header:
        #while appending text_body and html_body
        try:
            for message in mail_account.messages():
                msg =mailbox.mboxMessage()
                for key in dir(message):
                    value=getattr(message,key,None)
                    if(type(value)==str):
                        msg[key] = value
                mbox.add(msg)
                mbox.flush()
        finally:
            mbox.unlock()



    def do_task_per_message(self, message, args):
        if message.Message_ID:
            log.debug(message.Message_ID.strip())
        else:
            log.debug(message.Subject)
