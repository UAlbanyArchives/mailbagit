---
layout: page
title: PDF Derivatives
permalink: /pdf/
parent: Installing mailbagit
nav_order: 4
---

# PDF derivatives

Unless you're using a Docker image, mailbagit is unable to make PDF derivatives out-of-the-box. For this option to be available, you need to have either [wkhtmltopdf](https://wkhtmltopdf.org/) or [Google Chome](https://www.google.com/chrome/) installed and added to your `PATH`.

## wkhtmltopdf

Adding `wkhtmltopdf` or `wkhtmltopdf.exe` to your `PATH` will make the `pdf` derivative option available. You can test this with `wkhtmltopdf -V` or `wkhtmltopdf.exe -V`.

## Chrome Headless

Adding `chrome`, `chrome.exe` or `google-chrome` to your `PATH` will make the `pdf-chrome` derivative option available. You can test this with:
```
chrome https://archives.albany.edu/mailbag
chrome.exe chrome https://archives.albany.edu/mailbag
google-chrome chrome https://archives.albany.edu/mailbag
```

## Security concerns

Automatically converting the HTML within emails to PDFs can cause security vulnerabilities in some contexts. Since it is [no longer actively maintained](https://wkhtmltopdf.org/status.html), wkhtmltopdf does not recommend running it on user-supplied and unsanitized HTML.

* [File Inclusion Vulnerability](https://www.virtuesecurity.com/kb/wkhtmltopdf-file-inclusion-vulnerability-2/)

Using Google Chrome or running `mailbagit` in a [Docker container](({{ site.baseurl}}/docker)) may mitigate some, but not all of these concerns.

Essentially, both PDF and WARC derivatives require rendering the HTML bodies within email messages. This will send HTTP GET requests from your IP address for any `<img src="">`, `<iframe src="">`, or `<link href="">` included within the HTML, just as if you were to render a message in an email client without additional protections.

Since Mailbag is designed for email preservation, in many contexts it may be unlikely for you to encounter malicious emails designed specifically to cause issues with `mailbagit`. However, you are likely to come across [email trackers](https://www.nutshell.com/blog/email-tracking-pixels-101-how-do-tracking-pixels-work) so you should be aware of them and how they work.