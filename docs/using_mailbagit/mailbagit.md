---
layout: page
title: Mailbagit CLI
permalink: /mailbagit/
parent: Using mailbagit
nav_order: 1
---

# Using the `mailbagit` command line utility


When `mailbagit` in [installed]({{ site.baseurl }}/install), it makes the `mailbagit` command available in you command line. You should be able to run `mailbagit -h` in Terminal on macOS or Linux, or CMD.exe or Powershell on Windows.

![Screenshot of running the mailbagit command in Windows Powershell.]({{ site.baseurl }}/img/mailbagit-demo1.png)

You can download a [sample MBOX file]({{ site.baseurl }}/data/account.mbox) for testing.

## Examples

```
mailbagit path/to/inbox.mbox -i mbox -d pdf warc --mailbag-name account_name
```
> Packages an MBOX file at `path/to/inbox.mbox` into a mailbag named "account_name" with PDF and WARC derivatives for each message. `mailbagit` will attempt to use any `X-Folder` headers to arrange derivatives.

```
mailbagit path/to/export -i pst -d eml html pdf -m allfacstafflistserv
```
> Packages all the PST files found in `path/to/export` and any subfolders into a mailbag named "allfacstafflistserv" with EML, HTML, and PDF derivatives. `mailbagit` will attempt to use both the directory structure of the PSTs as well as the email folder tree within the PST(s) to arrange derivatives.

```
mailbagit path/to/directory -i eml -d pdf-chrome warc -mailbag-name fundraising_emails -r
```
> Packages all the EML files found in `path/to/directory` and any subfolders into a mailbag named "fundraising_emails" with PDF and WARC derivatives with the PDF derivatives using headless Chrome. `mailbagit` will use the both the directory structure of the EMLs as well as any `X-Folder` headers to arrange derivatives.

> This examples also uses the `-r` (dry-run) flag, which will parse all EML files, but will not move, change, or package them into a mailbag. If there are any parsing errors, this will write an error report to the  `fundraising_emails_errors` directory.

## Arguments

The arguments listed below can be entered in the command line when using `mailbagit`or entered in `mailbagit-gui` fields

### Mandatory Arguments

* **path**:
> A path to email to be packaged into a mailbag. This can be a single file or a directory containing a number of email exports.

* **-m --mailbag-name**: 
> This will be used as the directory name for the mailbag, or the filename if compression is used.
> Must be a valid directory or file name.

* **-i --input**:  
> File format to use  as input for a mailbag.
> Argument takes single input.
> e.g. `-i imap` or `-i pst`

* **-d --derivatives**:
> Specifies a single or list of derivative formats that mailbagit will create and package into the mailbag.
> Argument takes multiple inputs.
e.g. `-d eml pdf warc`


### Mailbagit Optional  Arguments

* **-r --dry-run**
> Performs a test run that will not alter any files other than writing an error report. When this flag is used, `mailbagit` parses all the email it is provide and formats derivatives as much as it can without writing anything to disk. If there are any error or warnings, this will create an error report with an `errors.csv` listing all issues as well as a full stack trace in a `.txt` file.

* **--css**
> Path to a CSS file to override the included CSS when creating PDF or HTML derivatives
> Argument takes single file path as input.

* **-c --compress**
> Compresses the mailbag as a ZIP, TAR, or TAR.GZ
e.g. `-c zip` or `-c tar.gz`

### Bagit-python arguments

Mailbagit also accepts most [bagit-python](https://github.com/LibraryOfCongress/bagit-python) arguments. Thus, you can provide arguments like `--processes 2` or arguments to add metadata such as `--source-organization University at Albany, SUNY` 

The only bag-python arguments that `mailbagit` does not support are `-log`, `-quiet`, `-validate`, `-fast`, and `-completeness_only`

If you would like to validate your mailbag, `mailbagit` comes with [bagit-python](https://github.com/LibraryOfCongress/bagit-python) installed. Thus, you can run:

```
bagit.py --validate /path/to/mailbag
```