# Mailbagit

A tool for creating and managing Mailbags, a package for preserving email in multiple formats. It contains an open [specification for mailbags](https://archives.albany.edu/mailbag/spec/), as well as the `mailbagit` and `mailbagit-gui` tools for packaging email exports into mailbags.

## Installation

```
pip install mailbagit
```

* To install PST dependancies: `pip install mailbagit[pst]`
* To install `mailbagit-gui`: `pip install mailbagit[gui]`

You can also run `mailbagit` using a [Docker image](https://archives.albany.edu/mailbag/docker).

## Quick start

Examples:

```
mailbagit path/to/messages -i msg --derivatives eml pdf warc --mailbag_name my_mailbag
```

```
mailbagit path/to/inbox.mbox -i mbox -d txt pdf-chrome -m my_mailbag -r
```

```
mailbagit path/to/export.pst -i pst -d mbox eml pdf warc -m my_mailbag
```

See the [documentation](https://archives.albany.edu/mailbag/use/) for more details on:

* [mailbagit](https://archives.albany.edu/mailbag/mailbagit/)
* [mailbagit-gui](https://archives.albany.edu/mailbag/mailbagit-gui/)
* [logging](https://archives.albany.edu/mailbag/logging/)
* [plugins](https://archives.albany.edu/mailbag/plugins/)


### Development setup

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
