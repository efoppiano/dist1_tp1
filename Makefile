SHELL := /bin/bash
PWD := $(shell pwd)

include .env
export

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