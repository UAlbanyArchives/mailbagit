import os
from structlog import get_logger
import mailbag.helper as helper
from warcio.capture_http import capture_http
from warcio import WARCWriter
import requests  # requests *must* be imported after capture_http
from threading import Thread
import http.server
import socketserver

log = get_logger()

from mailbag.derivative import Derivative


class WarcDerivative(Derivative):
    derivative_name = 'warc'
    derivative_format = 'warc'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()
        
        self.args = kwargs['args']
        mailbag_dir = kwargs['mailbag_dir']
        self.warc_dir = os.path.join(str(mailbag_dir),'warc')
        self.httpd = []

        if not self.args.dry_run:
            os.makedirs(self.warc_dir)

            self.server_thread = Thread(target=helper.startServer,args=(self.args.dry_run,self.httpd,5000))
            self.server_thread.start()

    def cleanup(self):
        log.debug("Calling server destructor")
        if not self.args.dry_run:
            helper.stopServer(self.args.dry_run,self.httpd[0])
        
        # Terminate the process
        try:
            if not self.args.dry_run:
                self.server_thread.join()
        except SystemExit:
            pass
        except:
            import traceback
            traceback.print_exc()
        
    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):
        if message.HTML_Body is None:
            log.warn("Error writing warc derivative for " + str(message.Mailbag_Message_ID))
        else:
            log.debug('self.warc_dir'+str(self.warc_dir))
            self.saveWARC(self.args.dry_run, self.warc_dir, message)            

    def saveWARC(self, dry_run, warc_dir, message, port=5000):
        message_warc_dir = os.path.join(warc_dir, str(message.Mailbag_Message_ID))
        filename = os.path.join(message_warc_dir, str(message.Mailbag_Message_ID) + ".warc.gz")
        
        log.debug("Writing warc derivative to " + filename)
        
        if not dry_run:
            os.mkdir(message_warc_dir)
            with capture_http(filename):
                helper.saveFile('tmp.html',message.HTML_Body)
                requests.get('http://localhost:' + str(port) + '/tmp.html')
            helper.deleteFile('tmp.html')
