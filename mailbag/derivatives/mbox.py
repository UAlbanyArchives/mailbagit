from structlog import get_logger
import email
import mailbox
import sys, os, string, re

log = get_logger()

from mailbag.derivative import Derivative
class MboxDerivative(Derivative):
    derivative_name = 'mbox'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self,mail_account,args):
        new_path = os.path.join(args.directory, args.mailbag_name,"derivative.mbox")
        mbox = mailbox.mbox(new_path)
        mbox.lock()
        #appending only header values to mbox file
        try:
            for message in mail_account.messages():
                msg = mailbox.mboxMessage()
                for key in message.Headers:
                    value = message.Headers[key]
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
