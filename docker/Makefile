migrate:
	docker-compose exec se-python python manage.py migrate

static:
	docker-compose up se-nodejs
	docker-compose exec se-python python manage.py excel
	docker-compose exec se-python python manage.py price
	docker-compose exec se-python python manage.py collectstatic --noinput

build: static
	docker-compose -f docker-compose-production.yml build

test: static
	docker-compose up -d se-selenium-hub
	docker-compose up -d se-redis
	docker-compose exec se-python python manage.py test --liveserver=se-python:8020-8030 --parallel=8
	docker-compose stop

