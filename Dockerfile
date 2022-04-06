FROM ubuntu:20.04
MAINTAINER Gregory Wiedeman gwiedeman@albany.edu

ENV TZ=America/New_York \
    DEBIAN_FRONTEND=noninteractive

RUN mkdir /code
WORKDIR /code
ADD Pipfile /code/

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential
RUN apt-get install -y python
RUN apt-get install -y python3-pip
RUN apt-get install -y curl
RUN apt-get install -y libgtk-3-dev

# Install Python dependancies
RUN pip install pipenv
RUN pipenv run pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
RUN pipenv install

# Install wkhtmltopdf
RUN curl -L -o /tmp/wkhtmltox_0.12.6-1.focal_amd64.deb \
	https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
RUN apt-get install -y /tmp/wkhtmltox_0.12.6-1.focal_amd64.deb

ADD . /code/
RUN pip shell
RUN pip install --no-dependencies -e .