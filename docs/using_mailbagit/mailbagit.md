---
layout: page
title: Mailbagit CLI
permalink: /mailbagit/
parent: Using mailbagit
nav_order: 1
---

# Using the `mailbagit` command line utility


When `mailbagit` is installed, it makes the `mailbagit` command available in you command line. `mailbagit -h` can run in Terminal on macOS or Linux, or CMD.exe or Powershell on Windows. [Download and install mailbagit]({{ site.baseurl }}/install).

![Screenshot of running the mailbagit command in Windows Powershell.]({{ site.baseurl }}/img/mailbagit-demo1.png)

[Download a sample MBOX file]({{ site.baseurl }}/data/account.mbox) for training and testing.

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

💡 `mailbagit` can also package the .ost file that the Microsoft Outlook desktop client uses to store email locally. OSTs are just treated as PSTs. If you use Outlook, you might be able to find your local OST file at `C:\Users\[username]\AppData\Local\Microsoft\Outlook`.

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

* **-v --version**
> Reports the version number and exits.

* **-r --dry-run**
> Performs a test run that will not alter any files other than writing an error report. When this flag is used, `mailbagit` parses all the email it is provide and formats derivatives as much as it can without writing anything to disk. If there are any error or warnings, this will create an error report with an `errors.csv` listing all issues as well as a full stack trace in a `.txt` file.

* **-k --keep**
> Keeps the source files as-is and copies instead of moving them into a mailbag.

* **--css**
> Path to a CSS file to override the included CSS when creating PDF or HTML derivatives
> Argument takes single file path as input.

* **-c --compress**
> Compresses the mailbag as a ZIP, TAR, or TAR.GZ
> e.g. `-c zip` or `-c tar.gz`

* **-f, --companion_files**
> Allows for companion metadata files to be packaged alongside email export files.
> When this option is used, `mailbagit` will recursively include all the files in the directory provided into a mailbag.

### Bagit-python arguments

Mailbagit also accepts most [bagit-python](https://github.com/LibraryOfCongress/bagit-python) arguments. Thus, you can provide arguments like `--processes 2` or arguments to add metadata such as `--source-organization University at Albany, SUNY` 

The only bag-python arguments that `mailbagit` does not support are `-log`, `-quiet`, `-validate`, `-fast`, and `-completeness_only`

If you would like to validate your mailbag, `mailbagit` comes with [bagit-python](https://github.com/LibraryOfCongress/bagit-python) installed. Thus, you can run:

```
bagit.py --validate /path/to/mailbag
```

## What `mailbagit` creates

`mailbagit` creates a "mailbag" according to the [Mailbag Specification]({{ site.baseurl }}/spec). The mailbag will be named using the provided `mailbag_name` and will be a folder, unless compression was used. In this folder, you will find a payload folder called “data” which contains the original export formats, as well as attachments, and any derivatives you selected.

Mailbags also contain one or more `mailbag.csv` files which list all messages that were packaged. The first column is “Error” where any  errors in the packaging are reported. If the message was parsed and generated derivatives successfully, this field will be blank. The Mailbag-Message-ID is a sequential ID number that is unique within a mailbag. This ID is used to name all the derivative files in the mailbag. `mailbag.csv` files also document the number of attachments and contain common email headers such as [Message-ID](https://en.wikipedia.org/wiki/Message-ID), To, From, CC, and Subject.

As valid "bags," according to the [Bagit specification](https://tools.ietf.org/html/rfc8493), mailbags also contain manifests containing checksums for all files within the bag. These checksums are useful to establish fixity or show that the files have not changed over time.

* `mailbagit` also generates detailed [error reports]({{ site.baseurl }}/errors) 
