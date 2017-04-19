UPDATE = bash -c '\
	python3 manage.py migrate \
	&& python3 manage.py excel \
	&& python3 manage.py price \
	&& python3 manage.py collectstatic --no-input \
'

define UP =
	docker-compose up -d $(1)
	docker-compose exec $(1) $(UPDATE)
endef

.PHONY: up_prod
up_prod:
	$(call UP,se_prod)

.PHONY: up_dev
up_dev:
	$(call UP,se_dev)

.PHONY: deploy
deploy:
	docker-compose pull
	$(foreach app,se_prod se_dev,$(call UP,$(app)))
