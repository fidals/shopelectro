FROM node:slim

ARG deps_dir
ENV DEPS_DIR=$deps_dir

WORKDIR /usr/app/src/

RUN apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y ssh git \
    && git clone https://github.com/fidals/refarm-site.git $DEPS_DIR \
    && apt-get remove --purge -y git \
    && apt-get -y --purge autoremove \
    && rm -rf /var/lib/apt/lists/*

# we use `--no-optional` because some optional npm dependencies fail on install
RUN npm install -g gulp-cli
# `npm install gulp-imagemin` don't install it's dependencies sometimes.
# Took decision from SO: https://goo.gl/3uXZxw
RUN npm install imagemin-jpegtran imagemin-svgo imagemin-gifsicle imagemin-optipng --save

COPY package.json package.json
RUN npm install --no-optional

COPY gulpfile.babel.js gulpfile.babel.js
COPY front/ front

# Keeps track of changes if static files are built, otherwise builds them
CMD bash -c "[ '$(ls -A /usr/app/src/build)' ] && gulp watch || (gulp build && gulp watch)"
