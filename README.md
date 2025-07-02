# MedAssistant

**MedAssistant** is a cloud-hosted platform for NFC-based traceability and environmental monitoring of pharmaceutical items. It integrates NFC scans, Wi-Fi sensors, real-time alerts, and an interactive web dashboard.

---

## 📁 Repository Structure

medassistant/                      ← root of your repo
├── .github/                       ← GitHub configuration
│   └── workflows/
│       ├── ci.yml                ← Tests & lint workflow
│       ├── build-and-push-ecr.yml← Docker build & ECR push
│       └── deploy_infra.yml      ← Terraform apply infra
│
├── backend/                       ← Backend service
│   ├── app/                       ← FastAPI source
│   │   ├── main.py               ← app entrypoint & start_scheduler()
│   │   ├── models.py             ← all SQLAlchemy models
│   │   ├── schemas.py            ← all Pydantic schemas
│   │   ├── auth_security.py      ← JWT auth & RBAC
│   │   ├── db_session.py         ← SQLAlchemy engine + SessionLocal
│   │   ├── routes/
│   │   │   ├── items.py          ← `/items` endpoints
│   │   │   ├── sensors.py        ← `/sensors/readings/` endpoint
│   │   │   ├── sensors_status.py ← `/sensors/status/` endpoint
│   │   │   └── alerts.py         ← `/alerts` endpoints
│   │   ├── services/
│   │   │   ├── item_service.py   ← `get_items` logic
│   │   │   ├── sensor_service.py ← `ingest_and_check` logic
│   │   │   └── alert_service.py  ← alert dispatch & rules
│   │   ├── scheduler.py          ← APScheduler jobs & start_scheduler()
│   │   └── infra/                ← your Terraform IaC
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   ├── Dockerfile                ← container spec
│   ├── requirements.txt          ← Python dependencies
│   └── tests/                    ← pytest suites
│       ├── test_sensor_service.py
│       ├── test_sensors_route.py
│       └── test_alert_service.py
│
├── frontend/                      ← React PWA
│   ├── public/                   ← static assets (favicon, index.html)
│   ├── src/
│   │   ├── components/           ← reusable UI parts
│   │   │   ├── InventoryTable.tsx
│   │   │   ├── SensorStatusPanel.tsx
│   │   │   └── AlertManagement.tsx
│   │   └── Dashboard.tsx         ← main dashboard page
│   ├── package.json              ← npm dependencies & scripts
│   └── tailwind.config.js        ← Tailwind setup
│
├── scripts/
│   └── seed.py                   ← initial DB seed script
│
├── docker-compose.yml            ← local dev orchestration
├── .env.example                  ← sample environment vars
└── README.md                     ← project overview & quick-start

---

## 🚀 Quick Start

### 1. Prerequisites

- **Docker** & **Docker Compose**  
- **Node.js** (v18+) & **npm**  
- **Terraform** (v1.2+)  
- AWS credentials with permissions to create VPC, RDS, ECR, ECS

### 2. Local Development

```bash
# Clone & scaffold
git clone <repo-url>
cd medassistant

# Start backend
cd backend
docker-compose up --build
# In another shell:
python scripts/seed.py

# Start frontend
cd ../frontend
npm install
npm run dev
Backend: http://localhost:8000

Frontend: http://localhost:3000

3. Testing
bash
# Backend tests & lint
cd backend
pip install -r requirements.txt
pytest
flake8 .

# Frontend lint & type-check
cd ../frontend
npm run lint
npm run type-check
📦 Docker & CI/CD
1. CI — .github/workflows/ci.yml
Runs on PR & main

Matrix: Python 3.9/3.10/3.11

Executes pytest and flake8

2. Build & Push — .github/workflows/build-and-push-ecr.yml
On main merge

Auth via AWS OIDC

Builds Docker image, tags with SHA & latest

Pushes to ECR

Exposes IMAGE_URI output

3. Infra Deploy — .github/workflows/deploy_infra.yml
On main merge

terraform init, plan, apply in backend/app/infra

Uses GitHub secrets for vars:

AWS_REGION, PROJECT_NAME

DB_USERNAME, DB_PASSWORD

ECR_REPOSITORY_NAME

🛠️ Environment Variables
Create a GitHub or local .env with:
# Backend
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/medassistant
SECRET_KEY=<jwt-secret>

# Terraform (via GH secrets or terraform.tfvars)
aws_region=us-east-1
project_name=medassistant
db_username=<db-user>
db_password=<db-pass>
ecr_repository_name=<ecr-repo>
🗓️ Deployment Flow
Merge to main → CI runs tests & lint

Build & Push image to ECR

Terraform Apply infra (VPC, RDS, ECS)

Seed DB (scripts/seed.py) via one-off job or manual

Smoke Test /health, /docs

Pilot Rollout
