import os
from structlog import get_logger
import mailbag.helper as helper
from warcio.capture_http import capture_http
from warcio import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
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
        self.warc_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        self.httpd = []

        if not self.args.dry_run:
            os.makedirs(self.warc_dir)

            self.server_thread = Thread(target=helper.startServer, args=(self.args.dry_run, self.httpd, 5000))
            self.server_thread.start()

    def terminate(self):
        
        # Terminate the process
        try:
            if not self.args.dry_run:
                helper.stopServer(self.args.dry_run, self.httpd[0])
                self.server_thread.join()
        except SystemExit:
            pass
        except:
            import traceback
            traceback.print_exc()
        
    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        if message.HTML_Body is None and message.Text_Body is None:
            log.warn("No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ". No HTML derivative will be created.")
        else:
            log.debug('self.warc_dir' + str(self.warc_dir))
            self.saveWARC(self.args.dry_run, self.warc_dir, message)            

    def saveWARC(self, dry_run, warc_dir, message, port=5000):
        out_dir = os.path.join(self.warc_dir, message.Derivatives_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".warc.gz")
        
        if not dry_run:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
    
            with open(filename, 'wb') as output:
                html_formatted, encoding = helper.htmlFormatting(message, self.args.css, headers=False)
                helper.saveFile('tmp.html', html_formatted)
                
                writer = WARCWriter(output, gzip=True)
                resp = requests.get('http://localhost:' + str(port) + '/tmp.html',
                                    headers={'Accept-Encoding': 'identity'},
                                    stream=True)
            
                # get raw headers from urllib3
                headers_list = resp.raw.headers.items()
            
                http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')
            
                record = writer.create_warc_record('http://localhost', 'response',
                                                    payload=resp.raw,
                                                    http_headers=http_headers)
                writer.write_record(record)
            helper.deleteFile('tmp.html')