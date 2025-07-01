#!/usr/bin/env bash

# Name of root folder and output ZIP
ROOT="medassistant"
ZIP_FILE="medassistant_package.zip"

# Clean up any previous scaffold or ZIP
rm -rf "$ROOT" "$ZIP_FILE"

# 1. Create directory structure
mkdir -p "$ROOT"/.github/workflows
mkdir -p "$ROOT"/backend/app/routes
mkdir -p "$ROOT"/backend/app/services
mkdir -p "$ROOT"/backend/app/infra
mkdir -p "$ROOT"/backend/tests
mkdir -p "$ROOT"/frontend/public
mkdir -p "$ROOT"/frontend/src/components
mkdir -p "$ROOT"/scripts

# 2. Create placeholder files

# GitHub workflows
touch "$ROOT"/.github/workflows/ci.yml
touch "$ROOT"/.github/workflows/build-and-push-ecr.yml
touch "$ROOT"/.github/workflows/deploy_infra.yml

# Backend app
touch "$ROOT"/backend/app/main.py
touch "$ROOT"/backend/app/db_session.py
touch "$ROOT"/backend/app/auth_security.py
touch "$ROOT"/backend/app/models.py
touch "$ROOT"/backend/app/schemas.py
touch "$ROOT"/backend/app/scheduler.py

# Backend routes
touch "$ROOT"/backend/app/routes/items.py
touch "$ROOT"/backend/app/routes/sensors.py
touch "$ROOT"/backend/app/routes/sensors_status.py
touch "$ROOT"/backend/app/routes/alerts.py

# Backend services
touch "$ROOT"/backend/app/services/item_service.py
touch "$ROOT"/backend/app/services/sensor_service.py
touch "$ROOT"/backend/app/services/alert_service.py

# Terraform infra
touch "$ROOT"/backend/app/infra/main.tf
touch "$ROOT"/backend/app/infra/variables.tf
touch "$ROOT"/backend/app/infra/outputs.tf

# Backend top-level
touch "$ROOT"/backend/Dockerfile
touch "$ROOT"/backend/requirements.txt

# Backend tests
touch "$ROOT"/backend/tests/test_sensor_service.py
touch "$ROOT"/backend/tests/test_sensors_route.py
touch "$ROOT"/backend/tests/test_alert_service.py

# Frontend placeholders
touch "$ROOT"/frontend/public/index.html
touch "$ROOT"/frontend/src/main.tsx
touch "$ROOT"/frontend/src/index.css
touch "$ROOT"/frontend/src/Dashboard.tsx
touch "$ROOT"/frontend/src/components/InventoryTable.tsx
touch "$ROOT"/frontend/src/components/SensorStatusPanel.tsx
touch "$ROOT"/frontend/src/components/AlertManagement.tsx
touch "$ROOT"/frontend/package.json
touch "$ROOT"/frontend/tailwind.config.js

# Scripts
touch "$ROOT"/scripts/seed.py

# Root config files
touch "$ROOT"/docker-compose.yml
touch "$ROOT"/.env.example
touch "$ROOT"/README.md

# 3. Package into ZIP
zip -r "$ZIP_FILE" "$ROOT"

echo "✔ Scaffolded and packaged into $ZIP_FILE"
