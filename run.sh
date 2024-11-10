#!/bin/bash
set -euo pipefail
source .env
docker compose -f docker-compose.yml -f docker-compose.local.yml -f metaservices.local.yml up -d --build --remove-orphans