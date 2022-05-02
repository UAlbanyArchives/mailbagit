FROM ubuntu:20.04
MAINTAINER Gregory Wiedeman gwiedeman@albany.edu

ARG APP_ENV=prod

ENV TZ=America/New_York \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential
RUN apt-get install -y python
RUN apt-get install -y python3-pip

# Install wxPython with dependancies
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 libnotify-dev
RUN pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython

# Install Optional Python dependancies
RUN pip install libpff-python==20211114

# Install wkhtmltopdf
RUN apt-get install -y curl
RUN curl -L -o /tmp/wkhtmltox_0.12.6-1.focal_amd64.deb \
	https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
RUN apt-get install -y /tmp/wkhtmltox_0.12.6-1.focal_amd64.deb

# Install chrome headless
RUN curl -L -o /tmp/google-chrome-stable_current_amd64.deb \
    https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y /tmp/google-chrome-stable_current_amd64.deb

RUN mkdir /mailbag
WORKDIR /mailbag
ADD . /mailbag/
WORKDIR /

RUN if [ "${APP_ENV}" = "dev" ] ; \
    then echo export MAILBAG_LOG_LEVEL='debug' >> ~/.bashrc && \
    # manually add to $PYTHONPATH because https://github.com/python/importlib_metadata/issues/364
    echo export PYTHONPATH='/mailbag' >> ~/.bashrc && \
    echo cd /mailbag >> ~/.bashrc && \
    cd /mailbag && \
    pip install -e . ; \
    else rm -rf /mailbag && \
    echo export MAILBAG_LOG_LEVEL='info' >> ~/.bashrc && \
    pip install mailbag ; \
    fi
