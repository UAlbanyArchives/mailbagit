FROM ubuntu:20.04
MAINTAINER Gregory Wiedeman gwiedeman@albany.edu

ENV TZ=America/New_York \
    DEBIAN_FRONTEND=noninteractive \
    MAILBAGIT_LOG_LEVEL=debug\
    IN_CONTAINER=true

RUN mkdir /mailbagit
WORKDIR /mailbagit
ADD . /mailbagit/

# manually add to $PYTHONPATH because https://github.com/python/importlib_metadata/issues/364
ENV PYTHONPATH=/mailbagit

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y curl

# needed to build some python libraries
RUN apt-get install -y gcc dpkg-dev

# wkhtmltopdf deps
RUN apt-get install -y xfonts-75dpi xfonts-base

RUN pip install libpff-python==20211114

RUN curl -L -o /tmp/google-chrome-stable_current_amd64.deb \
        https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y /tmp/google-chrome-stable_current_amd64.deb

RUN curl -L -o /tmp/wkhtmltox_0.12.6-1.buster_amd64.deb \ 
        https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb
RUN dpkg -i /tmp/wkhtmltox_0.12.6-1.buster_amd64.deb

RUN pip install -e .[pst]
