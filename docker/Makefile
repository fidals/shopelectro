migrate:
	docker-compose exec se-python python manage.py migrate

static:
	docker-compose run se-nodejs bash -c "npm install && npm install -g gulp-cli && gulp build"
	docker-compose exec se-python python manage.py excel
	docker-compose exec se-python python manage.py price
	docker-compose exec se-python python manage.py collectstatic --noinput

build-dev-py:
	docker-compose build --no-cache se-python

build: build-dev-py static
	docker-compose -f docker-compose-production.yml build

test: static
	docker-compose up -d se-selenium-hub
	docker-compose up -d se-redis
	docker-compose exec se-python python manage.py test --liveserver=se-python:8020-8030 --parallel
	docker-compose stop

lint:
	docker-compose up -d se-python
	docker run --rm --volumes-from se-python --workdir=/usr/app/src -it coala/base bash -c 'npm install -g eslint eslint-plugin-import eslint-config-airbnb-base && coala all.javascript --ci'
