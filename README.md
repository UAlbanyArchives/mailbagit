# Mailbag

A tool for creating and managing Mailbags, a package for preserving email in multiple formats

## Installation

`pip install mailbag`

### Working with PST files

Making mailbags from .pst files on Windows requires Visual Studio C++ Build Tools. This is also required for a development environment setup on Windows. 

1. Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/)
2. Using the Visual Studio installer, in the Workloads tab make sure to check "Desktop development with C++" and the VS 2019 C++ x64/x86 build tools in the Installation details optional settings on the right side.

![Screenshot of checking the correct options using the Visual Studio Installer.](windows_install.png)

### Development setup

mailbag is set up to use pipfile

```
git clone git@github.com:UAlbanyArchives/mailbag.git
cd mailbag
pipenv shell
pipenv install
pip install -e .
```

### wxPython install on Ubuntu

wxPython sometimes causes issues installing on some Linux distros. If you have issues on Ubuntu 20.04, try installing it directly with this package.

`pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython` 

## Tools

Mailbag contains multiple tools.

* `mailbagit` a command line tool for creating mailbags
* `mailbagit-gui` a basic graphical user interface which performs the same functions as `mailbagit` 
* a future tool for reporting the contents of mailbags

## Using `mailbagit` and `mailbagit-gui`

The arguments listed below can be entered in the command line when using `mailbagit`or entered in `mailbagit-gui` fields

#### `mailbagit` Examples

`mailbagit path/to/input.mbox --mailbag-name account_name -i mbox -d pdf warc`
`mailbagit path/to/input.pst --mailbag-name allfacstafflistserv -i pst -d eml pdf`
`mailbagit path/to/input/directory --mailbag-name fundraising_emails -i eml -d pdf`

### Mailbag Mandatory Arguments

* **directory/filepath**:
> The input MBOX or PST file, or a directory containing EML or MSG files.
> When creating mailbags from IMAP connections, this must be an existing directory where the mailbag will be created.

* **-m --mailbag-name**: 
> This will be used as the directory name for the mailbag, or the filename if compression is used.
> Must be a valid directory or file name.

* **-i --input**:  
> File format to use  as input for a mailbag.
> Argument takes single input.
e.g. `-i imap` `-i pst`

* **-d --derivatives**:
> Specifies a single or list of formats required as results from mailbag.
> Argument takes single input.
e.g. `-d eml pdf warc`


### Mailbag Optional  Arguments

* **--imap_host**:
> Hostname for an IMAP connection used to create a mailbag.
> Argument takes single input.

* **--imap_user**:
> User account for creating a mailbag from an IMAP connection
> Argument takes single input.

* **--imap_password**:
> Password for IMAP connection for mailbag.
> Argument takes single input.

* **--exclude_folder**:
> Email folders that need to be excluded from mailbag.
> Argument takes single or multiple folder names.
 e.g. `--exclude_folder Junk Trash`

* **--exclude_messages**:
> Email folders that need to be excluded from mailbag.
> Argument takes single or multiple Message-IDs as input.
>  e.g. `--exclude_messages <2f6a90a391c4499b8738c5d50a29d8de@carolynmaloney.com>`

* **-e --exclude_input**:
> Email folders and messages excluded while creating a mailbag will also be removed from the original source PST or MBOX
> Argument does not take any input.
> Applicable for PST and MBOX files.

* **-l --crawl_links**:
> Attempts to capture links in messages and include them in WARC derivatives.
> Argument does not take any input.

* **-a --crawl-attached-links**
> Attempts to capure links attached to messages and include them in WARC derivatives
> Argument does not take any input.

* **-n --no-headers**
> Will not include email headers in `mailbag.csv`
> Argument does not take any input.

* **--pdf-css**
> Path to a CSS file to override the included CSS when creating PDF derivatives
> Argument takes single file path as input.

* **-c --compress**
> Compresses the mailbag as a ZIP, TAR, or TAR.GZ
e.g. `-c tar.gz`

### Bagit-python arguments

Mailbag also accepts [bagit-python](https://github.com/LibraryOfCongress/bagit-python) arguments. Thus, you can provide arguments like `--processes 2` or arguments to add metadata such as `--source-organization University at Albany, SUNY` 


## Plugins

New formats (and eventually, other components) may be provided to mailbag to extend its functionality. You may also override the mailbag's built-in parsers. By default, mailbag will look for formats in the following places:

1. a `formats` subdirectory within a directory specified in the `MAILBAG_PLUGIN_DIR` environment variable.
	Unix Example:
	`mkdir ~/myplugindir`
	`mkdir ~/myplugindir/formats`
	`touch ~/myplugindir/formats/pst.py`
	`export MAILBAG_PLUGIN_DIR=$HOME/myplugindir`
2. a `.mailbag/formats` subdirectory in the user's home directory.
3. formats built into mailbag

## Logging

* The level of logs displayed by Mailbag is based on an environment variable `MAILBAG_LOG_LEVEL`.
Log levels are available in the following order : `NOTSET`, `DEBUG`, `INFO`, `WARN`, `ERROR`, and `CRITICAL`.
For example, when the `MAILBAG_LOG_LEVEL` is `DEBUG`, `Mailbag` displays logs of all levels.
And when `MAILBAG_LOG_LEVEL` is `WARN`, it displays logs of level `WARN` and above. i.e. `WARN`, `ERROR`, or `CRITICAL`.

* If no `MAILBAG_LOG_LEVEL` environment variable is set, mailbag will default to `WARN`.

* Example of the logger initiation and usage in `Python`:<br/><br/>
	`from structlog import get_logger`<br/>
	`import mailbag.loggerx`<br/>
	`loggerx.configure()`<br/>
	`log = get_logger()`<br/>	
	`log.error("Error message here")`<br/>
	`log.info("Information message here")`