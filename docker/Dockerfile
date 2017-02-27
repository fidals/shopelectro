# Docker confing inspired by this speech:
# http://www.moscowpython.ru/meetup/35/dokerizacija-prilozhenij-na-python/
#
# Boilerplate Django project on Docker from speech here:
# https://github.com/satyrius/paid


FROM ubuntu:16.10

# Installing Linux packages and global python packages (like gunicorn and circus).
RUN export DEBIAN_FRONTEND=noninteractive TERM=xterm \
    && locale-gen en_US.UTF-8 \
    && apt-get update -qq && apt-get upgrade -qq \

    # for nodejs
    && apt-get install -y --no-install-recommends curl \
    && curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get install -y nodejs npm \
    && ln -s /usr/bin/nodejs /usr/bin/node \

    && apt-get install -y --no-install-recommends \
        nginx-light \
        python3.6 \
        python3-pip \
        python3-setuptools \
        python3-psycopg2 \
        git \
        python-imaging libjpeg62 libjpeg62-dev \
        nano \
        emacs-nox \
        wget \

    && BUILD_DEPS='build-essential python3-dev' \
    && apt-get install -y --no-install-recommends ${BUILD_DEPS} \

    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir \
        circus==0.13.0 \
        gunicorn==19.5.0 \
        iowait==0.2 \
        psutil==4.2.0 \
        pyzmq==15.2.0 \
        tornado==4.3 \

    && apt-get autoremove -y ${BUILD_DEPS} \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set locales
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# Installing application dependencies from requirements.txt
COPY requirements.txt /opt/shopelectro/app/
RUN pip3 install --no-cache-dir -r /opt/shopelectro/app/requirements.txt

# Copying source code and nginx/gunicorn configs
COPY etc/ /etc/
COPY . /opt/shopelectro/app/

RUN chmod -R +x /opt/shopelectro/

# Running nginx, perform Django management commands.
WORKDIR /opt/shopelectro/app
ENV STATIC_ROOT=/opt/shopelectro/static
ENV MEDIA_ROOT=/opt/shopelectro/app/media

RUN nginx -t \
    && npm install -g gulp && npm install && gulp build \
    && python3 -c 'import compileall, os; compileall.compile_dir(os.curdir, force=1)' > /dev/null \
    && python3 ./manage.py collectstatic --settings=shopelectro.settings.prod --no-input -v0 \
    && chown -R www-data /opt/shopelectro/ \
