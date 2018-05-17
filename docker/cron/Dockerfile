FROM debian:latest

RUN apt-get update && apt-get install -y \
    cron \
    rsyslog

COPY etc/backup/crontab /etc/cron.d/crontab
COPY etc/backup/backup-entrypoint.sh /usr/bin/entrypoint.sh

CMD service rsyslog start && service cron start && tail -f /var/log/syslog
