dc=docker-compose
d=docker
dcb=$(dc) -f docker-compose-build.yml
dcp=$(dc) -f docker-compose-production.yml
# the same const value is used at `test_db` django command
TEST_DB=test_se

# @todo #269 Create docs for build system.

.PHONY: migrate create-env build-static watch-static \
build test backup restore \
generate-production-static-data deploy


# ---------------------- Dev section ----------------------
repl:
	$(dc) exec app python manage.py shell

bash:
	$(dc) exec app bash

migrate:
	$(dc) run --rm app python manage.py migrate

fixtures:
	$(dc) run --rm app bash -c "\
		python manage.py loaddata shopelectro/fixtures/admin.json \
		&& python manage.py loaddata shopelectro/fixtures/dump.json \
	"

gen-fixtures:
	$(dc) exec postgres bash -c "\
		psql -Upostgres <<< 'CREATE DATABASE $(TEST_DB);' \
	"
	$(dc) run --rm -e POSTGRES_DB=$(TEST_DB) app python manage.py test_db
	$(dc) exec postgres bash -c "\
		psql -Upostgres <<< 'DROP DATABASE $(TEST_DB);' \
	"

prices:
	$(dc) exec app python manage.py price

excel:
	$(dc) exec app python manage.py excel

create-env:
	@bash ./create-env.sh

create-config:
	@bash ./create-config.sh

npm-install:
	$(dcb) build --no-cache nodejs

build-static:
	$(dc) run --rm nodejs gulp build

watch-static:
	$(dc) run --rm nodejs

collectstatic:
	$(dc) exec app python manage.py collectstatic --noinput

test: build-static
	$(dc) up -d app selenium
	$(dc) exec app python manage.py test -v 3 --parallel
	$(dc) stop

lint-code:
	$(dc) run --rm lint

lint-pdd:
	$(dc) run --rm pdd

lint-pdd-verbose:
	$(dc) run --rm pdd --verbose

lint:
	$(MAKE) lint-code
	$(MAKE) lint-pdd

upd-dev:
	$(dc) up -d app

stop-prod-celery:
	$(dcp) stop celery-beat celery-command-worker celery-default-worker celery-mail-worker

upd-prod-celery:
	$(dcp) up -d celery-beat celery-command-worker celery-default-worker celery-mail-worker

upd-prod: upd-prod-celery
	$(dcp) up -d app nginx

deploy-dev:
	$(MAKE) create-env
	$(MAKE) create-config
	$(dc) pull
	$(dc) up -d app
	$(MAKE) build-static
	$(MAKE) migrate
	# Create admin user with login/pass: admin/asdfjkl;
	$(MAKE) fixtures
	# Launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(MAKE) collectstatic
    # to make fresh collected static visible immediately
	$(dc) stop app && $(MAKE) upd-dev

# update internationalization messages
i18n:
	@bash do-i18n.sh


# ---------------------- Production deploy section ----------------------
backup:
	$(dcp) run --rm backup-data sh /usr/bin/entrypoint.sh

restore:
	@bash ../etc/backup/backup-restore.sh

generate-production-static-data:
	$(dcp) exec app python manage.py excel
	$(dcp) exec app python manage.py price

# drone should do this in working flow.
# But if drone don't do this for some reasons,
# you can run this recipe from local machine.
prepare-deploy:
	rm -rf front/build
	$(dc) stop app && $(dcp) stop app
	$(dc) rm -f app && $(dcp) rm -f app
	$(MAKE) build-static
	$(dcb) build --no-cache python-dev python-prod
	$(dcb) push python-dev python-prod

deploy:
	$(dcp) stop
	# to flush nginx's inner static caches
	$(MAKE) stop-prod-celery
	$(dcp) rm -f app nginx && $(MAKE) upd-prod
	$(dcp) exec app python manage.py migrate
	$(dcp) exec app python manage.py custom_pages
	$(MAKE) -j generate-production-static-data
	# Launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dcp) exec app python manage.py collectstatic --noinput
	# to make fresh collected static visible immediately
	$(dcp) stop app nginx && $(dcp) up -d app nginx
