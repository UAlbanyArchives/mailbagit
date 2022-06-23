---
layout: page
title: Error and warning reports
permalink: /errors/
parent: Using mailbagit
nav_order: 3
---

# Error and warning reports

When there are issues during packaging `mailbagit` creates separate directories using the `-m` or `--mailbag-name` argument. `fundraising_emails_errors` and `fundraising_emails_warnings`, for example. These contain reports of any errors or warnings experienced during packaging. Within the reports directory `mailbagit` creates `errors.csv` or `warnings.csv` files listing all issues. Reports also include a `.txt` file for each message with an issue that contains a full stack trace when relevant. 

## Reports when using `--dry-run`

Mailbagit creates error and warning reports during a test run using the optional argument `-r` or `--dry-run`. We recommend using this argument first to show if anything unexpected will happen during packaging.

Most, but not all errors and warnings will be included in the reports during a test run. Using `--dry-run` fully parses the provided email messages, so any issues found there will be included. However a test run does not write anything to the filesystem, so errors or warnings that may happen during that process will not be included using `--dry-run`.

Examples of errors and warnings that are not included when using `--dry-run`:
	* Issues writing files or directories to disk
	* Issues when using `wkhtmltopdf` or `chrome --headless` to generate PDF derivatives
	* Issues when writing WARC derivatives, like 404 or 400 HTTP responses or SSL errors.

## Example Error report

	fundraising_emails/
	|    |
    |    +-- bagit.txt
    |    |
    |    +-- bag-info.txt
    |    |
    |    +-- mailbag.csv
    |    |
    |    ...
	fundraising_emails_errors/
    |    |
    |    +-- 136.txt
    |    |
    |    +-- 2284.txt
    |    |
    |    +-- errors.csv
    |     
    fundraising_emails_warnings/
         |
         +-- 25.txt
         |
         +-- 514.txt
         |
         +-- 835.txt
         |
         +-- 1485.txt
         |
         +-- 3263.txt
         |
         +-- warnings.csv


## Common Warnings

### 404s for external resources

`wkhtmltopdf` raises warnings when image URLs and other externally-hosted resources are not found (404) when a PDF is created. These raise a warning and are included in warnings reports when the `pdf` derivative option is selected. These warnings are not included when the `--dry-run` option is used.

     WARN: Error converting to 254.pdf: Loading pages (1/6)
     [>                                                           ] 0%
     [======>                                                     ] 10%
     [======>                                                     ] 10%
     [======>                                                     ] 10%
     [======>                                                     ] 10%
     [======>                                                     ] 10%
     [==========================>                                 ] 44%
     Error: Failed to load cid:1469322111, with network status code 301 and http status code 0 - Protocol "cid" is unknown
     [============================================================] 100%
     Counting pages (2/6)                                               
     [============================================================] Object 1 of 1
     Resolving links (4/6)                                                       
     [============================================================] Object 1 of 1
     Loading headers and footers (5/6)                                           
     Printing pages (6/6)
     [>                                                           ] Preparing
     [============================================================] Page 1 of 1
     Done                                                                      
     Exit with code 1 due to network error: ProtocolUnknownError
     .

`chrome --headless` DOES NOT raise any issues when 404s are found, so when the `pdf-chrome` derivative option is selected this information will not be including in any error or warning reports.

WARC derivatives generate warnings when external resources do not return a HTTP 200 response.

	WARN: When writing WARC derivative, HTTP 403 Forbidden for external resource https://www.example.com/.

### Missing message bodies

`No Body Present` is a warning that occurs when `mailbagit` finds a message that does not contain a HTML or plain text body.

	No HTML or plain text body for 524, no HTML derivative created.
