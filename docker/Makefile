# # Docs: https://www.gnu.org/software/make/manual/make.html

# # Consts
# DEPLOY-MAP = PULL UP UPDATE

# # Functions
# UP = docker-compose up -d $(1);

# PULL = docker-compose pull $(1);

# UPDATE = docker-compose exec $(1) bash -c \
# 	'python3 manage.py migrate \
# 	&& python3 manage.py excel \
# 	&& python3 manage.py price \
# 	&& python3 manage.py collectstatic --no-input;'

# DEPLOY = $(foreach func,$(DEPLOY-MAP),$(call $(func),$(1)))

# ifdef SE_REMOTE_SERVER
# 	REMOTE-DEPLOY = @ssh $(SE_REMOTE_SERVER) 'cd prog/shopelectro/docker && make deploy'
# else
# 	REMOTE-DEPLOY = @echo "Define SE_REMOTE_SERVER variables.\nexport SE_REMOTE_SERVER=..."
# endif

# # Recipes
# .PHONY: deploy
# deploy:
# 	$(call DEPLOY,se_prod)
# 	$(call DEPLOY,se_dev)

# # Define SE_REMOTE_SERVER variables in your enviroment 
# .PHONY: remote-deploy
# remote-deploy:
# 	$(call REMOTE-DEPLOY)

migrate:
	docker-compose exec se-python python manage.py migrate

static:
	docker-compose up se-nodejs
	docker-compose exec se-python python manage.py excel
	docker-compose exec se-python python manage.py price
	docker-compose exec se-python python manage.py collectstatic --noinput

build: static
	docker-compose -f docker-compose-production.yml build

test-env-up: static
	docker-compose up -d se-selenium-hub
	docker-compose up -d se-redis

test: test-env-up
	docker-compose exec se-python python manage.py test --liveserver=se-python:8020-8030 --parallel=8
	docker-compose stop

