FROM python:slim

WORKDIR /usr/app/src/

COPY requirements.txt requirements.txt

RUN apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y wget git \
	&& pip install -r requirements.txt \
	&& apt-get remove --purge -y git && apt-get -y --purge autoremove && rm -rf /var/lib/apt/lists/*
