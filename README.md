# Mailbagit

A tool for creating and managing Mailbags, a package for preserving email in multiple formats. It contains an open [specification for mailbags](https://archives.albany.edu/mailbag/spec/), as well as the `mailbagit` and `mailbagit-gui` tools for packaging email exports into mailbags.

`mailbagit` can be used to convert native email formats, such as PST, MSG, EML, and MBOX into PDF, HTML, WARC, and other formats and combines them into stable packages for preservation.

## Installation

```
pip install mailbagit
```

* To install PST dependancies: `pip install mailbagit[pst]`
* To install `mailbagit-gui`: `pip install mailbagit[gui]`

You can also run `mailbagit` using a [Docker image](https://archives.albany.edu/mailbag/docker).

## Quick start

### Examples:

MSG files to PDF, EML, and WARC

```
mailbagit path/to/messages -i msg --derivatives eml pdf warc --mailbag_name my_mailbag
```

MBOX to PDF and plain text

```
mailbagit path/to/mbox_dir -i mbox -d txt pdf-chrome -m my_mailbag -r
```

PST to PDF, MBOX, EML, and WARC

```
mailbagit path/to/export.pst -i pst -d mbox eml pdf warc -m my_mailbag
```
EML to PDF and WARC in another directory

```
mailbagit path/to/messages -i eml -d pdf warc -m /path/to/my_mailbag
```

See the [documentation](https://archives.albany.edu/mailbag/use/) for more details on:

* [mailbagit](https://archives.albany.edu/mailbag/mailbagit/)
* [mailbagit-gui](https://archives.albany.edu/mailbag/mailbagit-gui/)
* [logging](https://archives.albany.edu/mailbag/logging/)
* [plugins](https://archives.albany.edu/mailbag/plugins/)

## Arguments

The arguments listed below can be entered in the command line when using `mailbagit`or entered in `mailbagit-gui` fields

### Mandatory Arguments

* **path**:
> A path to email to be packaged into a mailbag. This can be a single file or a directory containing a number of email exports.

* **-m --mailbag**: 
> A new directory for the mailbag, such as `/path/to/my_mailbag`, or just `my_mailbag` to use the same location as the source email. Must be a valid directory or file name and must not already exist.

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

## Development setup

```
git clone git@github.com:UAlbanyArchives/mailbagit.git
cd mailbagit
git switch develop
pip install -e .
```

#### Development with docker

Build and run image

```
docker pull ualbanyarchives/mailbagit:dev
docker run -it ualbanyarchives/mailbagit:dev
```

## License
[MIT](LICENSE)

## Kudos

This project was made possible by funding from the University of Illinois's [Email Archives: Building Capacity and Community Project](https://emailarchivesgrant.library.illinois.edu/).

We owe a lot to the hard work that goes towards developing and maintaining the libraries `mailbagit` uses to parse email formats and make bags. We'd like to thank these awesome projects, without which `mailbagit` wouldn't be possible:  

* [extractMsg](https://github.com/TeamMsgExtractor/msg-extractor)
* [libpff](https://github.com/libyal/libpff)
* [bagit-python](https://github.com/LibraryOfCongress/bagit-python)

We'd also like to thank the [RATOM project](https://ratom.web.unc.edu/) whose documentation was super helpful in guiding us though some roadblocks.
