FROM python:3.6.2-alpine
RUN apk --update add \
    bash \
    git \
    dcron \
    && rm -rf /var/apk/cache/*

ARG uid=1000
RUN adduser -u $uid -D subfinder

ADD . /opt/subfinder
ADD docker/crontab /etc/cron.d/subfinder
WORKDIR /opt/subfinder
RUN cp config.py.dist config.py
RUN git submodule update --init
VOLUME /data
RUN chown subfinder:subfinder /opt/subfinder -R
RUN chown subfinder:subfinder /etc/cron.d/subfinder

CMD ["docker/run.sh"]
