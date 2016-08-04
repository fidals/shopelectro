# Docker confing inspired by this speech:
# http://www.moscowpython.ru/meetup/35/dokerizacija-prilozhenij-na-python/
#
# Boilerplate Django project on Docker from speech here:
# https://github.com/satyrius/paid


FROM ubuntu:16.04

RUN export DEBIAN_FRONTEND=noninteractive \
    && sed -i 's,http://archive.ubuntu.com/ubuntu/,mirror://mirrors.ubuntu.com/mirrors.txt,' /etc/apt/sources.list \
    # for nodejs
    && apt-get update -qq && apt-get upgrade -qq \
    && apt-get install -y --no-install-recommends curl \
    && curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get update -qq && apt-get upgrade -qq \
    && apt-get install -y nodejs npm \
    && ln -s /usr/bin/nodejs /usr/bin/node \

    && apt-get install -y --no-install-recommends \
        nginx-light \
        python3 \
        python3-pip \
        python3-setuptools \
        python3-psycopg2 \
        git \
        python-imaging libjpeg62 libjpeg62-dev \

    && BUILD_DEPS='build-essential python3-dev' \
    && apt-get install -y --no-install-recommends ${BUILD_DEPS} \

    && pip3 install --no-cache-dir \
        circus==0.13.0 \
        gunicorn==19.5.0 \
        iowait==0.2 \
        psutil==4.2.0 \
        pyzmq==15.2.0 \
        tornado==4.3 \

    && apt-get autoremove -y ${BUILD_DEPS} \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt /opt/shopelectro/app/
RUN pip3 install --no-cache-dir -r /opt/shopelectro/app/requirements.txt

COPY etc/ /etc/
COPY . /opt/shopelectro/app/

# for windows compatibility
RUN chmod -R +x /opt/shopelectro/

WORKDIR /opt/shopelectro/app
ENV STATIC_ROOT=/opt/shopelectro/static
ENV MEDIA_ROOT=/opt/shopelectro/app/media
RUN nginx -t \
    && npm install -g gulp && npm install && gulp build \
    && python3 -c 'import compileall, os; compileall.compile_dir(os.curdir, force=1)' > /dev/null \
    && python3 ./manage.py collectstatic --settings=shopelectro.settings.base --no-input -v0
CMD ["circusd", "/etc/circus/web.ini"]
