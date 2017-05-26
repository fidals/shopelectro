FROM python:slim

COPY requirements.txt /requirements.txt
ENV DEPS_DIR /usr/app/deps

RUN apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y wget git \
	&& pip install -t $DEPS_DIR -r requirements.txt \
	&& apt-get remove --purge -y git \
    && apt-get -y --purge autoremove \
    && rm -rf /var/lib/apt/lists/*

RUN export PYTHONPATH=$PYTHONPATH:$DEPS_DIR

WORKDIR /usr/app/src/
