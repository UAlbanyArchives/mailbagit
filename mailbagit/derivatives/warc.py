import os
import warcio
import mailbagit.helper.derivative as derivative
import mailbagit.helper.common as common
from warcio.capture_http import capture_http
from warcio import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import requests  # requests *must* be imported after capture_http
from threading import Thread
import http.server
import socketserver

from structlog import get_logger

log = get_logger()

from mailbagit.derivative import Derivative


class WarcDerivative(Derivative):
    derivative_name = "warc"
    derivative_format = "warc"
    try:
        from importlib import metadata
    except ImportError:  # for Python<3.8
        import importlib_metadata as metadata
    derivative_agent = warcio.__name__
    derivative_agent_version = metadata.version("warcio")

    def __init__(self, email_account, args, mailbag_dir):
        log.debug("Setup account")

        # Sets up self.format_subdirectory
        super().__init__(args, mailbag_dir)

        self.httpd = []
        self.port = 5000
        self.tmp_file = "tmp.html"

        if not self.args.dry_run:

            self.server_thread = Thread(target=derivative.startServer, args=(self.args.dry_run, self.httpd, self.port))
            # Make it a daemon so it will stop after ctrl+c
            self.server_thread.daemon = True
            self.server_thread.start()

    def terminate(self):

        # Terminate the process
        try:
            if not self.args.dry_run:
                derivative.stopServer(self.args.dry_run, self.httpd[0])
                self.server_thread.join()
        except SystemExit:
            pass
        except:
            import traceback

            traceback.print_exc()

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        errors = []

        try:

            if message.HTML_Body is None and message.Text_Body is None:
                desc = "No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ", no WARC derivative created"
                errors = common.handle_error(errors, None, desc, "warn")
            else:
                out_dir = os.path.join(self.format_subdirectory, message.Derivatives_Path)
                filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".warc.gz")
                log.debug("Writing WARC to " + str(filename))

                if not self.args.dry_run:
                    if not os.path.isdir(out_dir):
                        os.makedirs(out_dir)

                    with open(filename, "wb") as output:

                        try:
                            html_formatted, encoding = derivative.htmlFormatting(message, self.args.css, headers=False)
                            with open(self.tmp_file, "w", encoding="utf-8") as f:
                                f.write(html_formatted)
                                f.close()
                        except Exception as e:
                            desc = "Error formatting HTML for WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                        writer = WARCWriter(output, gzip=True)
                        try:
                            resp = requests.get(
                                "http://localhost:" + str(self.port) + "/" + self.tmp_file,
                                headers={"Accept-Encoding": "identity"},
                                stream=True,
                            )
                            resp.raise_for_status()

                        except requests.exceptions.HTTPError as e:
                            desc = "Error requesting HTML for WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            # get raw headers from urllib3
                            headers_list = resp.raw.headers.items()

                            http_headers = StatusAndHeaders("200 OK", headers_list, protocol="HTTP/1.0")

                            record = writer.create_warc_record(
                                "http://localhost:" + str(self.port) + "/" + self.tmp_file,
                                "response",
                                payload=resp.raw,
                                http_headers=http_headers,
                            )
                        except Exception as e:
                            desc = "Error writing WARC headers"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            writer.write_record(record)
                        except Exception as e:
                            desc = "Error writing WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                    output.close()
                    derivative.deleteFile(self.tmp_file)

        except Exception as e:
            desc = "Error creating WARC derivative"
            errors = common.handle_error(errors, e, desc)

        message.Errors.extend(errors)

        return message
