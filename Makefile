SHELL := /bin/bash
PWD := $(shell pwd)

compose_up_local:
	set -euo pipefail
	source .env
	docker compose -f docker-compose.yml -f metaservices.local.yml up -d --build --remove-orphans
.PHONY: compose_up_local


compose_down_local:
	set -euo pipefail
	docker compose -f docker-compose.yml -f metaservices.local.yml stop
	docker compose -f docker-compose.yml -f metaservices.local.yml down
.PHONY: compose_down_local
