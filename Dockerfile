FROM ubuntu:20.04
MAINTAINER Gregory Wiedeman gwiedeman@albany.edu

ENV TZ=America/New_York \
    DEBIAN_FRONTEND=noninteractive \
    MAILBAG_LOG_LEVEL=debug

RUN mkdir /mailbag
WORKDIR /mailbag
ADD requirements.txt /mailbag/

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential
RUN apt-get install -y python
RUN apt-get install -y python3-pip

# Install wxPython with dependancies
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 libnotify-dev
RUN pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython

# Install Python dependancies
RUN pip install -r requirements.txt

# Install wkhtmltopdf
RUN apt-get install -y curl
RUN curl -L -o /tmp/wkhtmltox_0.12.6-1.focal_amd64.deb \
	https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
RUN apt-get install -y /tmp/wkhtmltox_0.12.6-1.focal_amd64.deb

ADD . /mailbag/
RUN pip install -e .