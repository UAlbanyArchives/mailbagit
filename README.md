# Mailbag

A tool for creating and managing Mailbags, a package for preserving email in multiple formats. It contains an open specification for mailbags, as well as the `mailbagit` and `mailbagit-gui` tools for packaging email exports into mailbags.

## Installation

```
pip install mailbag
```

* To install PST dependancies: `pip install mailbag[pst]`
* To install `mailbagit-gui`: `pip install mailbag[gui]`

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

>>>>>>> develop
```
git clone git@github.com:UAlbanyArchives/mailbag.git
cd mailbag
pip install -e .
```

#### Development with docker

Build and run image

```
docker pull ualbanyarchives/mailbag:dev
docker run -it ualbanyarchives/mailbag:dev
```

#### Building a release

##### Building and pushing Docker images

```
docker build -t mailbag:latest -f Dockerfile.production .
docker build -t mailbag:dev .
docker push ualbanyarchives/mailbag:latest
docker push ualbanyarchives/mailbag:dev
```

## License
[MIT](LICENSE)