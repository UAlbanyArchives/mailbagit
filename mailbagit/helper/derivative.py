import os
import base64
import codecs
from bs4 import BeautifulSoup, Doctype

import http.server
import socketserver

from structlog import get_logger

log = get_logger()


def startServer(dry_run, httpdShared, port=5000):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    log.debug("Starting Server")
    if not dry_run:
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("127.0.0.1", port), QuietHandler) as httpd:
            httpdShared.append(httpd)
            httpd.serve_forever()


def stopServer(dry_run, httpd):
    log.debug("Stopping Server")
    if not dry_run:
        httpd.shutdown()
        httpd.server_close()


def deleteFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)


def htmlFormatting(message, external_css, headers=True):
    """
    Creates a formatted html file using message text or html body
    inserts any additional styling given by user
    Useful for html and pdf derivative

    Parameters:
        message:message object
        external_css(string): path of css file to customize derivative
        headers(boolean):option to add table of headers

    Returns:
        String: formatted html for pdf, html derivatives
    """

    # check to see which body to use
    html_content = False
    encoding = False
    if message.HTML_Body:
        html_content = message.HTML_Body
        encoding = message.HTML_Encoding
    elif message.Text_Body:
        #  converting text body to html body
        html_content = (
            """
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        #mailbagPlainText{white-space: pre;}
                    </style>
                </head>
                <body>
                    <section id='mailbagPlainText'>"""
            + message.Text_Body
            + """<section>
                </body>
            </html>
        """
        )
        # using utf-8 for ascii plain text bodies as we're adding non-ascii whitespace
        if codecs.lookup(message.Text_Encoding).name.lower() == "ascii":
            log.debug("Using utf-8 to better handle whitespace for plain text ascii body message " + str(message.Mailbag_Message_ID))
            encoding = "utf-8"
        else:
            encoding = message.Text_Encoding
    else:
        log.warn("Unable to format HTML, no message body found for " + str(message.Mailbag_Message_ID))

    if html_content:

        # Formatting HTML with beautiful soup
        soup = BeautifulSoup(html_content.encode(encoding), "html.parser", from_encoding=encoding)

        # Checking if message contains partial html
        if not soup.html:
            html_content = "<html>" + html_content + "</html>"
            soup = BeautifulSoup(html_content.encode(encoding), "html.parser", from_encoding=encoding)
        if not soup.head:
            head = soup.new_tag("head")
            soup.html.insert(0, head)
        if not soup.body:
            body = soup.new_tag("body")
            soup.head.next_element.wrap(body)

        # Check Doctype
        doctype = False
        for item in soup.contents:
            if isinstance(item, Doctype):
                doctype = True
        if doctype is False:
            tag = Doctype("html")
            soup.insert(0, tag)

        # optionally adds headers table to html
        if headers:
            # Make headers table
            table = "<table id='mailbagHeadersTable'>"
            if message.Subject:
                h2 = "<h2>" + message.Subject + "</h2>"
            else:
                h2 = ""
            # Headers to display
            headerFields = [
                "Mailbag_Message_ID",
                "Message_ID",
                "From",
                "Date",
                "To",
                "Cc",
                "Bcc",
                "Subject",
            ]
            # Getting the values of the attrbutes and appending to HTML string
            for headerField in headerFields:
                value = getattr(message, headerField)
                if not value is None and value != []:
                    table += "<tr>"
                    table += "<td class='header'>" + str(headerField) + "</td>"
                    table += "<td>" + str(getattr(message, headerField)).replace("<", "&lt;").replace(">", "&gt;") + "</td>"
                    table += "</tr>"
            if len(message.Attachments) > 0:
                attachmentNumber = len(message.Attachments)
                table += "<tr>"
                table += "<td class='header'>Attachments</td><td>"
                for i, attachment in enumerate(message.Attachments):
                    table += attachment.Name
                    if i + 1 < attachmentNumber:
                        table += "<br/>"
                table += "</td>"
                table += "</tr>"
            tableSection = "<section id='mailbagHeaders'>" + h2 + table + "</table></section>"
            soupTable = BeautifulSoup(tableSection, "html.parser")

            # Add headers table to HTML body
            soup.body.insert(0, soupTable)

        # Embedding Encoding with meta
        meta = soup.new_tag("meta")
        meta["charset"] = "utf-8"
        soup.head.insert(0, meta)

        # Embedding default styling
        default_css = """
            @media print {
                /* for Chrome margins */
                @page { margin: 10; }
            }
            section#mailbagHeaders table#mailbagHeadersTable {
                width: 100%;
                margin-bottom: 35px;
                text-align: left;
                border-top: 4px solid #000000;
                padding-top: 8px;
                border-collapse: separate;
                border-spacing: 0 1px;
            }
            section#mailbagHeaders table#mailbagHeadersTable > tbody > tr > td {
                font: 16px Arial sans-serif;
                color:  #000000;
                padding: 2px 5px;
            }
            section#mailbagHeaders table#mailbagHeadersTable tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            section#mailbagHeaders h2 {
                margin-bottom: 2px;
                font-size: 24px;
                font-family: Arial sans-serif;
        """
        style = soup.new_tag("style")
        style.string = default_css
        soup.head.append(style)

        # Adding external_css
        if external_css:
            link = soup.new_tag("link")
            link["rel"] = "stylesheet"
            link["type"] = "text/css"
            link["href"] = "file:///" + external_css
            soup.head.append(link)

        # Embedding Images
        # HT to extract_msg for this approach
        # https://github.com/TeamMsgExtractor/msg-extractor/blob/6bed8213de1a7a41739fcf5c9363322508711fce/extract_msg/message_base.py#L403-L414
        tags = (tag for tag in soup.findAll("img") if tag.get("src") and tag.get("src").startswith("cid:"))
        data = None
        for tag in tags:
            # Iterate through the attachments until we get the right one.
            cid = tag["src"][4:]

            for attachment in message.Attachments:
                if attachment.Name in cid:
                    data = attachment.File

            # If we found anything, inject it.
            if data:
                tag["src"] = (b"data:image;base64," + base64.b64encode(data)).decode(encoding)

        html_content = soup.prettify(encoding).decode(encoding)

    return html_content, encoding
