FROM python:3.6.2-alpine
COPY requirements.txt /usr/src/app
RUN apk --update add git && rm -rf /var/apk/cache/*
RUN pip install --no-cache-dir -r requirements.txt
RUN git submodule update --init
RUN cp config.yml.dist config.yml