migrate:
	docker-compose exec se-python python manage.py migrate

static:
	@docker-compose run --rm se-nodejs bash -c "\
		npm install && \
		npm install -g gulp-cli && \
		gulp build"
	@docker-compose run --rm se-python bash -c "\
		python manage.py excel && \
		python manage.py price && \
		python manage.py collectstatic --noinput"

build-dev-py:
	@docker-compose build --no-cache se-python

build: build-dev-py static
	@docker-compose -f docker-compose-production.yml build

test: static
	@docker-compose up -d se-python se-selenium
	@docker-compose exec se-python python manage.py test -v 3 --liveserver=se-python:8020-8030 --parallel
	@docker-compose stop

backup:
	@docker-compose -f docker-compose-production.yml up se-backup-data

lint:
	@docker run --rm --volumes-from se-python --workdir=/usr/app/src -it coala/base coala
