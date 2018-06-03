dc=docker-compose
d=docker
dcb=$(dc) -f build/docker-compose.yml
dcp=$(dc) -f docker-compose-production.yml

# @todo #269 Create docs for build system.

.PHONY: migrate create-env build-static watch-static \
build test backup restore \
generate-production-static-data deploy


# --- Dev section ---
migrate:
	$(dc) run --rm app python manage.py migrate

fixtures:
	$(dc) run --rm app bash -c "\
		python manage.py loaddata shopelectro/fixtures/admin.json \
		&& python manage.py loaddata shopelectro/fixtures/dump.json \
	"

prices:
	$(dc) exec app python manage.py price

excel:
	$(dc) exec app python manage.py excel

create-env:
	@bash ./create-env.sh

build-static:
	$(dc) run --rm nodejs gulp build

watch-static:
	$(dc) run --rm nodejs gulp watch

collectstatic:
	$(dc) exec app python manage.py collectstatic --noinput

build:
	# Build nodejs image and static files
	$(dcb) build --no-cache nodejs
	$(MAKE) build-static
	# Build python image with sources and static files
	$(dcb) build --no-cache python-dev

test: build-static
	$(dc) up -d app selenium
	$(dc) exec app python manage.py test -v 3 --liveserver=app:8020-8030 --parallel=2
	$(dc) stop

lint:
	$(dc) up -d app
	$(dc) run --rm lint
	$(dc) stop


# --- Deploy section ---
deploy-dev:
	$(MAKE) create-env
	$(dc) pull
	$(dc) up -d app
	$(MAKE) build-static
	# Create admin user with login/pass: admin/asdfjkl;
	# Launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dc) exec app bash -c "\
		python manage.py migrate \
		&& python manage.py loaddata shopelectro/fixtures/admin.json \
		&& python manage.py loaddata shopelectro/fixtures/dump.json \
		&& python manage.py collectstatic --noinput \
	"
	$(dc) stop app
	$(dc) up -d app

# for production environment
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
	$(dcp) pull
	$(dcp) stop
	$(dcp) rm -f app nginx
	$(dcp) up -d app nginx
	$(dcp) exec app python manage.py migrate
	$(MAKE) -j generate-production-static-data
	# Launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dcp) exec app python manage.py collectstatic --noinput
	# to make fresh collected static visible immediately
	$(dcp) stop && $(dcp) up -d
