# Docs: https://www.gnu.org/software/make/manual/make.html

# Consts
DEPLOY-MAP = PULL UP UPDATE

# Functions
UP = docker-compose up -d $(1);

PULL = docker-compose pull $(1);

UPDATE = docker-compose exec $(1) bash -c \
	'python3 manage.py migrate \
	&& python3 manage.py excel \
	&& python3 manage.py price \
	&& python3 manage.py collectstatic --no-input;'

DEPLOY = $(foreach func,$(DEPLOY-MAP),$(call $(func),$(1)))

ifdef SE_REMOTE_SERVER
	REMOTE-DEPLOY = @ssh $(SE_REMOTE_SERVER) 'cd prog/shopelectro/docker && make deploy'
else
	REMOTE-DEPLOY = @echo "Define SE_REMOTE_SERVER variables.\nexport SE_REMOTE_SERVER=..."
endif

# Recipes
.PHONY: deploy
deploy:
	$(call DEPLOY,se_prod)
	$(call DEPLOY,se_dev)

# Define SE_REMOTE_SERVER variables in your enviroment 
.PHONY: remote-deploy
remote-deploy:
	$(call REMOTE-DEPLOY)
