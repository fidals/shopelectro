dc=docker-compose
d=docker
dcp=docker-compose -f docker-compose-production.yml

migrate:
	$(dc) exec se-python python manage.py migrate

# for local env
static:
	$(dc) pull se-nodejs
	$(dc) run --rm se-nodejs bash -c "\
		npm install -g gulp-cli && \
		# we use `--no-optional` because some optional npm dependencies fail on install
		npm install --no-optional && \
		gulp build"

# full version of this recipe will be developed in #248
# for local env
build:
	$(dc) build --no-cache se-python  # fetch <DEPS>/refarm-site/front/ dir
	$(dc) pull
	$(MAKE) static

test: static
	$(dc) up -d se-python se-selenium
	$(dc) exec se-python python manage.py test -v 3 --liveserver=se-python:8020-8030 --parallel
	$(dc) stop

backup:
	@docker-compose -f docker-compose-production.yml up se-backup-data

restore:
	@bash ../etc/se-backup-restore.sh

lint:
	$(dc) up -d se-python
	$(d) run --rm --volumes-from se-python --workdir=/usr/app/src -it coala/base coala
	$(dc) stop

# start dev environment
dev:
	$(dc) pull se-python
	$(dc) up -d se-python
	$(dc) exec se-python python manage.py migrate
	# launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dc) exec se-python python manage.py collectstatic --noinput
	$(dc) stop && $(dc) up -d  # to make fresh collected static visible immediately

# for serv env
deploy: backup
	$(dcp) pull
	$(dcp) stop
	$(dcp) rm -f se-source
	$(dcp) up -d
	$(dcp) exec se-python python manage.py migrate
	$(dcp) exec se-python python manage.py excel
	$(dcp) exec se-python python manage.py price
	# launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dcp) exec se-python python manage.py collectstatic --noinput
	$(dcp) stop && $(dcp) up -d  # to make fresh collected static visible immediately
