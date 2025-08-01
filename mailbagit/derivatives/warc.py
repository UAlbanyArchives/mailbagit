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
from requests.exceptions import ChunkedEncodingError
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

    def validate_url(self, url, errors):
        """
        Checks if a url is valid and has http/https schema before its requested and raises a warning if invalid or has a different schema.

        Parameters:
            url(str): A urls found within an email or external html page.
            errors (List): List of Error objects defined in models.py

        Returns:
            errors (List): List of Error objects defined in models.py
        """
        try:
            result = urllib.parse.urlparse(url)
            check = all([result.scheme, result.netloc])
            if result.scheme.lower().strip().startswith("http"):
                return True
            else:
                desc = f"When writing WARC derivative, skipping URL with non-http/https schema: {url}"
                errors = common.handle_error(errors, None, desc, "warn")
                return False
        except Exception as e:
            desc = f"When writing WARC derivative, skipping invalid URL: {url}"
            errors = common.handle_error(errors, None, desc, "warn")
            return False

    def html_external_resources(self, soup, url):
        """
        Reads an HTML body string and looks for all externally-hosted resources

        Parameters:
            soup(obj): A BeautifulSoup object
            url(str): A string of the URL from where the object was requested

        Returns:
            List: A deduplicated list of URLs
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
                else:
                    full_url = urllib.parse.urljoin(url, tag.get(attr))
                    external_urls.append(full_url)

        return list(dict.fromkeys(external_urls))

    def css_external_resources(self, cssText, cssURL):
        """
        Reads an CSS text and looks for all externally-hosted resources
        in properties, such as "@import url()" or "background-image: url()"

        Parameters:
            cssText(str): A string of CSS

        Returns:
            List: A deduplicated list of URLs
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

        return list(dict.fromkeys(external_urls))

    def crawl_external_urls(self, session, request_headers, warc_writer, urls, errors):
        """
        Reads a list of urls and crawls them and addes them to a WARC file.
        Parameters:
            session(str): The requests session
            request_headers(dict): A dict of request headers.
            warc_writer(WARCWriter): a warcio WARC writer object for writing pages to a WARC
            urls(list): A list of urls to crawl and add to a WARC.
            errors (List): List of Error objects defined in models.py

        Returns:
            session(str): The requests session
            warc_writer(WARCWriter): a warcio WARC writer object for writing pages to a WARC
            url_page_requisites(list): A de-duplicated list page_requisites like CSS and JS that also need to be crawled
            errors (List): List of Error objects defined in models.py
        """
        url_page_requisites = []
        i = 0
        for url in urls:
            log.debug("capturing " + url)
            # validate url
            if self.validate_url(url, errors):
                with capture_http(warc_writer):
                    # First try with SSL verification. If fails, raise a warning and turn off
                    try:
                        r = session.get(url, headers=request_headers, stream=True, timeout=20)
                        try:
                            content = r.content  # force load to detect errors
                        except ChunkedEncodingError as e:
                            desc = f"ChunkedEncodingError for {url}, retrying without stream."
                            errors = common.handle_error(errors, e, desc, "warn")
                            # Retry without streaming
                            r = session.get(url, headers=request_headers, stream=False, timeout=20)
                            content = r.content
                        if r.status_code != 200:
                            desc = f"When writing WARC derivative, HTTP {r.status_code} {r.reason} for external resource {url}"
                            errors = common.handle_error(errors, None, desc, "warn")

                        if "content-type" in r.headers:
                            if "text/html" in r.headers["content-type"]:
                                new_soup = BeautifulSoup(content, "html.parser")
                                new_external_urls = self.html_external_resources(new_soup, r.url)
                                url_page_requisites.extend(new_external_urls)
                            elif r.headers["content-type"] == "text/css":
                                new_external_urls = self.css_external_resources(content.decode("utf-8", errors="ignore"), r.url)
                                url_page_requisites.extend(new_external_urls)

                    except requests.exceptions.RequestException as e:
                        desc = f"Failed to request external URL for WARC derivatives ({url})"
                        errors = common.handle_error(errors, e, desc)
            i += 1
        return session, warc_writer, list(dict.fromkeys(url_page_requisites)), errors

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

                # Try to use Message_ID for WARC-Target-URI if present, otherwise
                if message.Message_ID is None or len(message.Message_ID) < 1:
                    warc_uri = f"http://mailbag/{str(message.Mailbag_Message_ID)}"
                else:
                    # strip leading and trailing brackets and add mailto: URI scheme
                    if message.Message_ID.startswith("<") and message.Message_ID.endswith(">"):
                        warc_uri = "mailto:" + message.Message_ID[1:-1]
                    else:
                        warc_uri = "mailto:" + message.Message_ID

                # Write Headers to UTF-8 JSON
                try:
                    headers = {}
                    for key in message.Headers:
                        headers[key], errors = format.parse_header(message.Headers[key], errors)
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
                        warc_writer = WARCWriter(output, gzip=True)
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
                            record = warc_writer.create_warc_record(
                                f"{warc_uri}/body.html",
                                "response",
                                payload=BytesIO(html_formatted.encode("utf-8")),
                                length=len(html_formatted.encode("utf-8")),
                                http_headers=http_headers,
                                warc_content_type="text/html",
                            )
                            warc_writer.write_record(record)
                        except Exception as e:
                            desc = "Error creating WARC response record for HTML body"
                            errors = common.handle_error(errors, e, desc)

                        # Write external resources
                        try:
                            s = requests.Session()
                            request_headers = {
                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
                            }

                            # Crawl external URLs
                            s, warc_writer, page_requisites, errors = self.crawl_external_urls(
                                s, request_headers, warc_writer, external_urls, errors
                            )

                            # Crawl external URL page requisites
                            s, warc_writer, new_page_requisites, errors = self.crawl_external_urls(
                                s, request_headers, warc_writer, page_requisites, errors
                            )

                        except Exception as e:
                            desc = "Error capturing external URL in WARC derivative"
                            errors = common.handle_error(errors, e, desc)

                        # Write attachments
                        try:
                            for i, attachment in enumerate(message.Attachments):
                                headers_list = [
                                    ("Content-Type", attachment.MimeType),
                                    ("Content-ID", attachment.Content_ID),
                                    ("Filename", attachment.WrittenName),
                                    ("Content-Length", str(len(attachment.File))),
                                    ("Date", datetime_to_http_date(datetime.now())),
                                ]
                                http_headers = StatusAndHeaders("200 OK", headers_list, protocol="HTTP/1.0")
                                record = warc_writer.create_warc_record(
                                    f"{warc_uri}/{quote_plus(attachment.WrittenName)}",
                                    "response",
                                    payload=BytesIO(attachment.File),
                                    length=len(attachment.File),
                                    http_headers=http_headers,
                                    warc_content_type="text/html",
                                )
                                warc_writer.write_record(record)
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
                            record = warc_writer.create_warc_record(
                                f"{warc_uri}/headers.json",
                                "response",
                                payload=BytesIO(headers_json),
                                length=len(headers_json),
                                http_headers=http_headers,
                                warc_content_type="application/json",
                            )
                            warc_writer.write_record(record)
                            record = warc_writer.create_warc_record(
                                f"{warc_uri}/headers.json",
                                "metadata",
                                payload=BytesIO(headers_json),
                                length=len(headers_json),
                                warc_content_type="application/json",
                            )
                            warc_writer.write_record(record)
                        except Exception as e:
                            desc = "Error creating JSON metadata record to WARC derivative"
                            errors = common.handle_error(errors, e, desc)

        except Exception as e:
            desc = "Error creating WARC derivative"
            errors = common.handle_error(errors, e, desc)

        message.Errors.extend(errors)

        return message
