FROM node:slim

ARG front_build_dir
ARG deps_dir
ENV DEPS_DIR=$deps_dir
ENV FRONT_BUILD_DIR=$front_build_dir

# Also this directory differs from $SRC_DIR to avoid `node_modules/` volumes conflicts.
WORKDIR /usr/app/src_front/

RUN apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y ssh git \
    && git clone https://github.com/fidals/refarm-site.git $DEPS_DIR \
    && apt-get remove --purge -y git \
    && apt-get -y --purge autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package.json
COPY gulpfile.babel.js gulpfile.babel.js

# we use `--no-optional` because some optional npm dependencies fail on install
RUN npm install -g gulp-cli
# `npm install gulp-imagemin` don't install it's dependencies sometimes.
# Took decision from SO: https://goo.gl/3uXZxw
RUN npm install imagemin-jpegtran imagemin-svgo imagemin-gifsicle imagemin-optipng --save
RUN npm install --no-optional
RUN gulp build
