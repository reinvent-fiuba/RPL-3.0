#!/bin/bash
set -euo pipefail
docker compose -f docker-compose.yml -f docker-compose.local.yml -f metaservices.local.yml stop
docker compose -f docker-compose.yml -f docker-compose.local.yml -f metaservices.local.yml down
