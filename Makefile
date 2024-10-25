SHELL := /bin/bash

clean-up: clean up

clean: down rm-imgs

down:
	cd ./setup/compose/; \
	docker compose down

rm-imgs: ./setup/.env ./setup/images/build.sh
	source ./setup/.env; \
	cd ./setup/images/; \
	./rm.sh $$PREFIX $$NUM_DBS $$NUM_APIS

up: build-imgs build-compfile
	cd ./setup/compose/; \
	docker compose up

build-imgs: ./setup/.env ./setup/images/build.sh
	source ./setup/.env; \
	cd ./setup/images/; \
	./build.sh $$PREFIX $$NUM_DBS $$NUM_APIS

build-compfile: ./setup/compose/build.sh
	source ./setup/.env; \
	cd ./setup/compose/; \
	./build.sh $$PREFIX $$NUM_DBS $$NUM_APIS