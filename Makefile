SHELL := /bin/bash
PWD := $(shell pwd)

default: build

all:

docker-compose-up: docker-compose-down
	docker compose --env-file .env -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

docker-compose-stop:
	docker compose -f docker-compose-dev.yaml stop -t 10
.PHONY: docker-compose-stop

docker-compose-down: docker-compose-stop
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs

docker-compose-ps:
	docker compose -f docker-compose-dev.yaml ps
.PHONY: docker-compose-ps

client-logs:
	docker compose -f docker-compose-dev.yaml logs client
.PHONY: client-logs

client-logs-live:
	docker compose -f docker-compose-dev.yaml logs client -f
.PHONY: client-logs-live