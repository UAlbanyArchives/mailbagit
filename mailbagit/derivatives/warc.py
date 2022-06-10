import os
import warcio
import mailbagit.helper.derivative as derivative
import mailbagit.helper.common as common
import mailbagit.helper.format as format
from warcio.capture_http import capture_http
from warcio import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import requests  # requests *must* be imported after capture_http
import json
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

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

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.warc_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        self.httpd = []
        self.port = 5000

        if not self.args.dry_run:
            os.makedirs(self.warc_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        errors = []

        try:

            if message.HTML_Body is None and message.Text_Body is None:
                desc = "No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ", no WARC derivative created"
                errors = common.handle_error(errors, None, desc, "warn")
            else:
                out_dir = os.path.join(self.warc_dir, message.Derivatives_Path)
                filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".warc")
                log.debug("Writing WARC to " + str(filename))

                # This is used for the WARC-Target-URI in the WARC derivatives
                warc_uri = f"http://{self.args.mailbag_name}-{str(message.Mailbag_Message_ID)}"

                # Write Headers to UTF-8 JSON
                try:
                    headers = {}
                    for key in message.Headers:
                        headers[key] = format.parse_header(message.Headers[key])
                    headers_json = json.dumps(headers, indent=4, sort_keys=True).encode("utf-8")
                except Exception as e:
                    desc = "Error formatting headers as UTF-8 JSON"
                    errors = common.handle_error(errors, e, desc)

                # Format HTML for WARC file
                try:
                    html_formatted, encoding = derivative.htmlFormatting(message, self.args.css, headers=False)
                except Exception as e:
                    desc = "Error formatting HTML for WARC derivative"
                    errors = common.handle_error(errors, e, desc)

                # Parse HTML for external resources
                external_urls = []
                soup = BeautifulSoup(html_formatted, "html.parser")
                external_resources = {"img": "src", "link": "href", "object": "data", "source": "src"}
                for tag in external_resources.keys():
                    attr = external_resources[tag]
                    for tag in soup.findAll(tag):
                        if tag.get(attr) and tag.get(attr).lower().strip().startswith("http"):
                            external_urls.append(tag.get(attr))
                # If external links option is selected, also crawl <a> urls and their external resources
                if self.args.external_links:
                    for a_tag in soup.findAll("a"):
                        if tag.get("href") and tag.get("href").lower().strip().startswith("http"):
                            external_urls.append(tag.get("href"))
                            print(tag.get("href"))

                if not self.args.dry_run:
                    if not os.path.isdir(out_dir):
                        os.makedirs(out_dir)

                    with open(filename, "wb") as output:
                        writer = WARCWriter(output, gzip=False)

                        try:
                            http_headers = StatusAndHeaders("200 OK", [("Content-Type", 'text/html; charset="utf-8"')], protocol="HTTP/1.0")
                            record = writer.create_warc_record(
                                f"{warc_uri}/body.html",
                                "response",
                                payload=BytesIO(html_formatted.encode("utf-8")),
                                length=len(html_formatted.encode("utf-8")),
                                http_headers=http_headers,
                                warc_content_type="text/html",
                            )
                            writer.write_record(record)
                        except Exception as e:
                            desc = "Error creating WARC response record for HTML body"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            for resource_url in external_urls:
                                # First try with SSL verification. If fails, raise a warning and turn off
                                try:
                                    resp = requests.get(
                                        resource_url,
                                        headers={"Accept-Encoding": "identity"},
                                        stream=True,
                                    )
                                except:
                                    desc = f"Failed to request external URL for WARC derivatives ({resource_url}). Retrying without SSL verification"
                                    errors = common.handle_error(errors, None, desc, "warn")
                                    import urllib3

                                    urllib3.disable_warnings()
                                    resp = requests.get(
                                        resource_url,
                                        headers={"Accept-Encoding": "identity"},
                                        stream=True,
                                        verify=False,
                                    )
                                # get raw headers from urllib3
                                headers_list = resp.raw.headers.items()
                                http_headers = StatusAndHeaders("200 OK", headers_list, protocol="HTTP/1.0")
                                record = writer.create_warc_record(
                                    resource_url,
                                    "response",
                                    payload=resp.raw,
                                    http_headers=http_headers,
                                )
                                writer.write_record(record)
                        except Exception as e:
                            desc = "Error capturing external URL in WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            for attachment in message.Attachments:
                                headers_list = [
                                    ("Content-Type", attachment.MimeType),
                                    ("Content-ID", attachment.Content_ID),
                                    ("Filename", attachment.Name),
                                ]
                                http_headers = StatusAndHeaders("200 OK", headers_list, protocol="HTTP/1.0")
                                record = writer.create_warc_record(
                                    f"{warc_uri}/{quote_plus(attachment.Name)}",
                                    "response",
                                    payload=BytesIO(attachment.File),
                                    length=len(attachment.File),
                                    http_headers=http_headers,
                                    warc_content_type="text/html",
                                )
                                writer.write_record(record)
                        except Exception as e:
                            desc = "Error adding attachments to WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                        try:
                            record = writer.create_warc_record(
                                f"{warc_uri}/headers.json",
                                "metadata",
                                payload=BytesIO(headers_json),
                                length=len(headers_json),
                                warc_content_type="application/json",
                            )
                            writer.write_record(record)
                        except Exception as e:
                            desc = "Error creating JSON metadata record to WARC derivative"
                            errors = common.handle_error(errors, e, desc)

        except Exception as e:
            desc = "Error creating WARC derivative"
            errors = common.handle_error(errors, e, desc)

        message.Errors.extend(errors)

        return message
