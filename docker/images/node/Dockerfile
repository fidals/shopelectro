FROM node:slim

WORKDIR /usr/app/src/

COPY package.json package.json

# we use `--no-optional` because some optional npm dependencies fail on install
RUN npm install -g gulp-cli && npm install --no-optional
