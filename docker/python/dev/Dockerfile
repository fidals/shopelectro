FROM python:slim

RUN apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y wget git make \
    && apt-get remove --purge -y git \
    && apt-get -y --purge autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /usr/app/src/
