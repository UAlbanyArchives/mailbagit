import os
import warcio
import cssutils
import logging
import mailbagit.helper.derivative as derivative
import mailbagit.helper.common as common
import mailbagit.helper.format as format
from warcio.capture_http import capture_http
from warcio import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from warcio.timeutils import datetime_to_http_date
import requests  # requests *must* be imported after capture_http
import json
import urllib.parse
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from datetime import datetime

from mailbagit.loggerx import get_logger

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
        log.debug(f"Setup {self.derivative_name} derivatives")

        # Sets up self.format_subdirectory
        super().__init__(args, mailbag_dir)

    def email_external_resources(self, soup):
        """
        Reads an HTML body string and looks for all externally-hosted
        resources in tags that are supported by email clients

        Parameters:
            soup(obj): A BeautifulSoup object

        Returns:
            List: A list of URLs
        """
        external_urls = []
        external_resources = {"img": "src", "link": "href", "object": "data", "source": "src"}
        for tag in external_resources.keys():
            attr = external_resources[tag]
            for tag in soup.findAll(tag):
                if tag.get(attr) and tag.get(attr).lower().strip().startswith("http"):
                    external_urls.append(tag.get(attr))

        return external_urls

    def html_external_resources(self, soup):
        """
        Reads an HTML body string and looks for all externally-hosted resources

        Parameters:
            soup(obj): A BeautifulSoup object

        Returns:
            List: A list of URLs
        """
        external_urls = []
        # not sure if this is comprehensive but something like "for tag in soup.find_all()"
        # was waaay too slow
        external_resources = {
            "img": "src",
            "link": "href",
            "area": "href",
            "base": "href",
            "object": "data",
            "source": "src",
            "script": "src",
            "iframe": "src",
            "embed": "src",
            "input": "src",
            "track": "src",
        }
        for tag in external_resources.keys():
            attr = external_resources[tag]
            for tag in soup.findAll(tag):
                if tag.get(attr) and tag.get(attr).lower().strip().startswith("http"):
                    external_urls.append(tag.get(attr))

        return external_urls

    def css_external_resources(self, cssText, cssURL):
        """
        Reads an CSS text and looks for all externally-hosted resources
        in properties, such as "@import url()" or "background-image: url()"

        Parameters:
            cssText(str): A string of CSS

        Returns:
            List: A list of URLs
        """

        external_urls = []
        cssutils.log.setLevel(logging.CRITICAL)
        css = cssutils.parseString(cssText)
        for rule in css:
            if hasattr(rule, "href"):
                external_urls.append(rule.href)
            elif hasattr(rule, "style"):
                for prop in rule.style:
                    value = prop.value.lower().strip()
                    if value.startswith("url(") and value.endswith(")"):
                        url = prop.value[4:][:-1]
                        if url.lower().startswith('"data'):
                            pass
                        elif url.lower().startswith("http"):
                            external_urls.append(url)
                        else:
                            external_urls.append(urllib.parse.urljoin(cssURL, url))

        return external_urls

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
                errors = common.check_path_length(out_dir, errors)
                errors = common.check_path_length(filename, errors)
                log.debug("Writing WARC to " + str(filename))

                # This is used for the WARC-Target-URI in the WARC derivatives
                warc_uri = f"http://mailbag/{str(message.Mailbag_Message_ID)}"

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
                soup = BeautifulSoup(html_formatted, "html.parser")
                external_urls = self.email_external_resources(soup)
                # If external links option is selected, also crawl <a> urls and their external resources
                if self.args.external_links:
                    for a_tag in soup.findAll("a"):
                        if a_tag.get("href") and a_tag.get("href").lower().strip().startswith("http"):
                            external_urls.append(a_tag.get("href"))

                if not self.args.dry_run:
                    if not os.path.isdir(out_dir):
                        os.makedirs(out_dir)

                    with open(filename, "wb") as output:
                        writer = WARCWriter(output, gzip=True)
                        # Write HTML Body
                        try:
                            headers_list = [
                                ("Content-Type", 'text/html; charset="utf-8"'),
                                ("Date", datetime_to_http_date(datetime.now())),
                                ("Content-Length", str(len(html_formatted.encode("utf-8")))),
                            ]
                            if message.Date:
                                headers_list.append(("Last-Modified", message.Date))
                            http_headers = StatusAndHeaders("200 OK", headers_list, protocol="HTTP/1.0")
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

                        # Write external resources
                        try:
                            s = requests.Session()
                            request_headers = {
                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
                            }
                            i = 0
                            while i < len(external_urls):
                                log.debug("capturing " + external_urls[i])
                                with capture_http(writer):
                                    # First try with SSL verification. If fails, raise a warning and turn off
                                    try:
                                        r = s.get(external_urls[i], headers=request_headers)
                                        if r.status_code != 200:
                                            desc = f"When writing WARC derivative, HTTP {r.status_code} {r.reason} for external resource {external_urls[i]}"
                                            errors = common.handle_error(errors, None, desc, "warn")
                                        if "content-type" in r.headers.keys():
                                            if r.headers["content-type"] == "text/html":
                                                # Gotta get these external resources as well
                                                new_soup = BeautifulSoup(r.text, "html.parser")
                                                new_external_urls = self.html_external_resources(new_soup)
                                                external_urls.extend(new_external_urls)
                                            elif r.headers["content-type"] == "text/css":
                                                new_external_urls = self.css_external_resources(r.text, r.url)
                                                external_urls.extend(new_external_urls)
                                    except Exception as e:
                                        desc = f"Failed to request external URL for WARC derivatives ({external_urls[i]})"
                                        errors = common.handle_error(errors, e, desc)
                                i += 1
                        except Exception as e:
                            desc = "Error capturing external URL in WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                        # Write attachments
                        try:
                            for attachment in message.Attachments:
                                headers_list = [
                                    ("Content-Type", attachment.MimeType),
                                    ("Content-ID", attachment.Content_ID),
                                    ("Filename", attachment.Name),
                                    ("Content-Length", str(len(attachment.File))),
                                    ("Date", datetime_to_http_date(datetime.now())),
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

                        # Write headers
                        try:
                            headers_list = [
                                ("Content-Type", "application/json"),
                                ("Date", datetime_to_http_date(datetime.now())),
                                ("Content-Length", str(len(headers_json))),
                            ]
                            http_headers = StatusAndHeaders("200 OK", headers_list, protocol="HTTP/1.0")
                            record = writer.create_warc_record(
                                f"{warc_uri}/headers.json",
                                "response",
                                payload=BytesIO(headers_json),
                                length=len(headers_json),
                                http_headers=http_headers,
                                warc_content_type="application/json",
                            )
                            writer.write_record(record)
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
