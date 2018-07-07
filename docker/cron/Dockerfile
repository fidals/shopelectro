FROM debian:latest

RUN apt-get update && apt-get install -y cron

COPY etc/backup/crontab /etc/cron.d/crontab
COPY etc/backup/backup-entrypoint.sh /usr/bin/entrypoint.sh

CMD service cron start && sleep infinity
