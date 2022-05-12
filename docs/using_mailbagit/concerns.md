---
layout: page
title: Privacy and security concerns
permalink: /concerns/
parent: Using mailbagit
nav_order: 6
---

# Privacy and security concerns

## File Inclusions in PDFs and WARCs

Automatically converting the HTML within emails to PDFs and WARCs can cause security vulnerabilities in some contexts. Since it is [no longer actively maintained](https://wkhtmltopdf.org/status.html), wkhtmltopdf does not recommend running it on user-supplied and unsanitized HTML.

* [File Inclusion Vulnerability](https://www.virtuesecurity.com/kb/wkhtmltopdf-file-inclusion-vulnerability-2/)

These issues primarily apply when running wkhtmltopdf in a web application where a potentially malicious user has access to the PDFs that are generated. Using Google Chrome may mitigate a few of these vulnerabilities, but overall shares most of these risks. This also applies to WARC derivatives.

We don't suggest using `mailbagit` in a web application, as a malicious email may leak information about the computer used to used to process it into a PDF. Since `mailbagit` is designed for email preservation, in many contexts it may be unlikely for you to encounter malicious emails designed specifically to cause issues with `mailbagit`, but it is still helpful to be aware of this issue. Running `mailbagit` in a [Docker container](({{ site.baseurl}}/docker)) mitigates many of these concerns.

## Email Trackers

Additionally, both PDF and WARC derivatives require rendering the HTML bodies for every email message packaged by `mailbagit`. This will send HTTP GET requests from your IP address for any `<img src="">`, `<iframe src="">`, or `<link href="">` included within the HTML, just as if you were to view each message in an email client without additional protections. You are likely to come across [email trackers](https://www.nutshell.com/blog/email-tracking-pixels-101-how-do-tracking-pixels-work) so you should be aware of them and how they work.

Running `mailbagit` in a [Docker container](({{ site.baseurl}}/docker)) by default uses its own IP address which is different than your host computer, but depending on how your network is set up, it still may ping all these URLs from your network IP. You might look into proxy servers if this is a concern.