---
layout: page
title: PDF Derivatives
permalink: /pdf/
parent: Installing mailbagit
nav_order: 3
---

# PDF derivatives

Unless you're using a Docker image, mailbagit is unable to make PDF derivatives out-of-the-box. For this option to be available, you need to have either [wkhtmltopdf](https://wkhtmltopdf.org/) or [Google Chome](https://www.google.com/chrome/) installed and added to your `PATH`.

[Learn more about `PATH` on Windows](https://www.maketecheasier.com/what-is-the-windows-path/).

⚠️ Creating PDF or WARC derivatives may cause [privacy or security concerns]({{ site.baseurl }}/concerns) in some contexts.

## wkhtmltopdf

Installing [wkhtmltopdf](https://wkhtmltopdf.org/) and adding `wkhtmltopdf` or `wkhtmltopdf.exe` to your `PATH` will make the `pdf` derivative option available. You can test this by entering `wkhtmltopdf -V` or `wkhtmltopdf.exe -V` into a command line terminal, which should show options for wkhtmltopdf.

## Chrome Headless

Installing [Google Chrome](https://www.google.com/chrome/) and adding `chrome`, `chrome.exe` or `google-chrome` to your `PATH` will make the `pdf-chrome` derivative option available. If you have Google Chrome installed already, you may just need to add it to your `PATH`.

For Windows, Chrome usually installs in one of these locations by default:
```
C:\Program Files\Google\Chrome\Application
C:\Program Files (x86)\Google\Chrome\Application
```

You can test if Chrome is correctly added to your `PATH` by entering the correlating command into a command line terminal:

```
chrome https://archives.albany.edu/mailbag
chrome.exe https://archives.albany.edu/mailbag
google-chrome https://archives.albany.edu/mailbag
```

If any of these commands open a Chrome browser window, you're all set!
