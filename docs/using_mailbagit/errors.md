---
layout: page
title: Error and warning reports
permalink: /errors/
parent: Using mailbagit
nav_order: 7
---

# Error and warning reports

Mailbagit optional argument `-r` or `--dry-run` creates error or warning reports during a test run.  

When there are errors `mailbagit` creates a directory using the `-m` or `--mailbag-name` argument. `fundraising_emails_errors`, for example. Within the directory `mailbagit`  creates an error report with an errors.csv listing all issues as well as a full stack trace in a .txt file.  

When there are warnings 'mailbagit' creates a directory using the `-m` or `--mailbag-name` argument. `fundraising_emails_warnings`, for example. Within the directory `mailbagit` creates a warning report with an warnings.csv listing all issues as well as a full stack trace in a .txt file. Both csvs contain the same fields as the mailbagit.csv.

## Common Warnings
`wkhtmltopdf` raises warnings when image URLs are not found (404) when a PDF is created.  

`No Body Present` is a warning that occurs when a message subject is found but `mailbagit` doesn't parse any message text.