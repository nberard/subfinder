#!/bin/bash

CRONTAB_PATH=/etc/cron.d/subfinder

LINE="*/1 * * * * cd /opt/subfinder && ./synchro_subtitles.py /data >> /var/log/synchro_subtitles.log 2>&1"
echo "$LINE" >> $CRONTAB_PATH
echo "" >> $CRONTAB_PATH

echo "Crontab created:"
cat $CRONTAB_PATH

touch /var/log/cron.log
touch /var/log/synchro_subtitles.log
chown subfinder:subfinder /var/log/synchro_subtitles.log
crontab -u subfinder $CRONTAB_PATH
crond -L /var/log/cron.log
tail -f /var/log/cron.log /var/log/synchro_subtitles.log
