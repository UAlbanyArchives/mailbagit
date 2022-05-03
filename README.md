# Mailbag

A tool for creating and managing Mailbags, a package for preserving email in multiple formats

## Installation

There a a couple different ways to install and run mailbagit.

1. Native python install with pip
2. Using Windows executables
3. Using a Docker image

### Native Python Install

`pip install mailbag`

#### Working with PST files

Packaging mailbags from .pst files requires additional dependancies. In addition to `pip install mailbag`, you need to run:

`pip install mailbag[pst]`

Installing this on Windows requires Visual Studio C++ Build Tools. Without this you will get an error.

1. Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/)
2. Using the Visual Studio installer, in the Workloads tab make sure to check "Desktop development with C++" and the VS 2019 C++ x64/x86 build tools in the Installation details optional settings on the right side.

![Screenshot of checking the correct options using the Visual Studio Installer.](windows_install.png)

#### Using the Mailbagit Graphical User Interface (GUI)

To install the mailbagit GUI, in addition to `pip install mailbag`, you need to run:

`pip install mailbag[gui]`

If it is installed correctly, the GUI will run using the `mailbagit-gui` command. There is a [known issue](https://github.com/UAlbanyArchives/mailbag/issues/155) where the GUI does not fully run on Windows. It will boot and lets you enter options but then fails to run when you click "start." Instead, try creating a file called `mailbagit-gui.py` with the contents:

```
from mailbag import gui
gui()
```

You should then be able to run the GUI with `python3 mailbagit-gui.py`.

##### GUI on Ubuntu

The GUI dependency wxPython does not install well on some environments, including Ubuntu. If `pip install mailbag[gui]` fails, you may want to try a [specific version for your distro](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/).

For example, on Ubuntu 20.04, this seems to work well.

`pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython`

After wxPython is installed, try running `pip install mailbag[gui]` again.

### Windows Executables

Executables are available for Windows that contain all dependencies except the PDF dependencies. Download the latest `mailbagit.exe` and `mailbagit-gui.exe` files from the [Github releases](https://github.com/UAlbanyArchives/mailbag/releases).

These executables are unsigned, so Windows will likely give you as "Windows protected your PC" warning from Microsoft Defender SmartScreen. You will need sufficient permissions to allow unsigned executables on you machine.


## PDF derivatives

Unless you're using a Docker image, mailbagit is unable to make PDF derivatives out-of-the-box. For this option to be available, you need to have either [wkhtmltopdf](https://wkhtmltopdf.org/) or [Google Chome](https://www.google.com/chrome/) installed and added to your `PATH`.

Adding `wkhtmltopdf` or `wkhtmltopdf.exe` to your `PATH` will make the `pdf` derivative option available. You can test this with `wkhtmltopdf -V` or `wkhtmltopdf.exe -V`.

Adding `chrome`, `chrome.exe` or `google-chrome` to your `PATH` will make the `pdf-chrome` derivative option available. You can test this with:
```
chrome https://archives.albany.edu/mailbag
chrome.exe chrome https://archives.albany.edu/mailbag
google-chrome chrome https://archives.albany.edu/mailbag
```


### Development setup

```
git clone git@github.com:UAlbanyArchives/mailbag.git
cd mailbag
pip install -e .
```

#### Docker setup

Build and run image
```
docker build -t mailbag .
docker run -it mailbag bash
```

Build and run development image
```
docker build -t mailbag:dev --build-arg APP_ENV=dev .
docker run -it mailbag:dev bash

docker build -t mailbag:dev .
docker build -t mailbag -f Dockerfile.production .
```

Build with access to host filesystem. Mailbagit will have access to the directory listed in the `source=` argument.

Examples:
```
docker run -it --mount type=bind,source="path/to/data",target=/data mailbag:dev bash
docker run -it --mount type=bind,source="C:\Users\Me\path\to\data",target=/data mailbag:dev bash
```

List running containers: `docker ps`
List images: `docker images`
Delete image: `docker image rm <image id> -f`


### wxPython install on Ubuntu

wxPython sometimes causes issues installing on some Linux distros. If you have issues on Ubuntu 20.04, try installing it directly with this package.

`pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython` 

#### wxPython dependencies

wxPython has dependencies that you may or may not have installed already. So if you get errors, you may need these:

```
sudo apt-get install libgtk-3-dev libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 libnotify-dev
```


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

* **--css**
> Path to a CSS file to override the included CSS when creating PDF or HTML derivatives
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