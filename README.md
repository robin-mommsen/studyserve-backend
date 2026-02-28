# studyserve-backend

Backend of **StudyServe** — a university project that lets students provision and manage virtual machines and containerized services through a self-service web platform.

The entire backend was designed and built by me alone, while other team members worked on the frontend, documentation, and infrastructure.

Users can create servers or services, start and stop them, organize them into projects, invite team members, and receive login credentials via e-mail — all through a REST API. Infrastructure is provisioned automatically using Terraform and configured with Ansible, running on Hetzner Cloud.

> **Note:** This repository is a mirror of the original private GitLab instance. The full commit history lives there. GitLab-specific files (`.gitlab-ci.yml`, etc.) can be ignored here.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2 + Django REST Framework |
| Database | PostgreSQL (via psycopg2) |
| Auth | Keycloak (JWT via drf-keycloak) |
| Async Tasks | Django-Q2 |
| Infrastructure | Terraform 1.12, Ansible |
| Cloud Provider | Hetzner Cloud |
| Containerization | Docker, Docker Compose |
| CI/CD | GitLab CI (build → deploy, 3 environments) |
| E-Mail | django-mailer with configurable SMTP backend |

---

## Architecture

The project is structured as a set of independent Django apps, each responsible for one domain:

```
server/
├── config/              # Django settings, URL routing, WSGI/ASGI
├── core/                # Shared base models, pagination, task hooks, mail utils
├── infra/Terraform/     # Terraform and Ansible orchestration layer
├── user_api/            # Custom user model, Keycloak claim mapping
├── project_api/         # Projects, members, invitations
├── server_api/          # VM lifecycle (create, start, stop, shutdown, delete)
├── server_config_api/   # VM configuration templates (size, script)
├── service_api/         # Containerized service lifecycle
├── service_config_api/  # Service configuration templates
└── management_api/      # Admin tools: credits, logs, maintenance messages, scheduler
```

### Infrastructure Flow

When a user creates a server via the API, the following happens asynchronously:

1. A Django-Q task is queued
2. The `Terraformer` class writes a `.tf` file, runs `terraform init`, `validate`, `plan`, and `apply`
3. Terraform provisions a VM on Hetzner Cloud
4. Ansible configures the VM (installs the requested service/script)
5. The task hook updates the server record with IP address, status, and world ID
6. The user receives login credentials by e-mail

Deletion follows the same pattern in reverse.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/servers/` | List own servers / create a new server |
| GET/PATCH/DELETE | `/api/servers/<id>/` | Retrieve, update or delete a server |
| POST | `/api/servers/<id>/action/<action>/` | Start, stop or shut down a server |
| GET | `/api/servers/<id>/logs/` | Retrieve logs for a server |
| GET/POST | `/api/services/` | List own services / create a new service |
| GET/PATCH/DELETE | `/api/services/<id>/` | Retrieve, update or delete a service |
| POST | `/api/services/<id>/action/<action>/` | Start, stop or shut down a service |
| GET/POST | `/api/projects/` | List own projects / create a project |
| GET/PATCH/DELETE | `/api/projects/<id>/` | Retrieve, update or delete a project |
| POST | `/api/projects/<id>/invite/` | Invite a user to a project |
| GET/POST | `/api/server-configs/` | List / create server configuration templates |
| GET/POST | `/api/service-configs/` | List / create service configuration templates |
| GET | `/api/users/` | List users |
| GET | `/api/management/` | Admin: credits, logs, platform settings |
| GET | `/api/maintenance-messages/` | Public maintenance messages |

All endpoints require a valid Keycloak JWT. Role-based access is enforced via scoped permission classes per HTTP method.

---

## Local Setup

### Prerequisites

- Docker & Docker Compose
- A running Keycloak instance
- A PostgreSQL database

### 1. Clone and configure

```bash
git clone https://github.com/robin-mommsen/studyserve-backend.git
cd studyserve-backend
cp .env.example .env
# Fill in your values in .env
```

### 2. Run with Docker Compose

```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`.

### 3. Run migrations

```bash
docker exec -it <container_name> python manage.py migrate
```

---

## CI/CD Pipeline

The GitLab CI pipeline has two stages — **BUILD** and **DEPLOY** — and supports three environments triggered by branch:

| Branch | Environment | Port |
|---|---|---|
| `development` | dev | 7003 |
| `staging` | staging | 7103 |
| `main` | production | 7203 |

On each push, the pipeline builds a Docker image, pushes it to the private registry, and deploys it to the target server via SSH and `docker compose up`.

---

## Environment Variables

See `.env.example` for a full list. Key variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DB_*` | PostgreSQL connection details |
| `KEYCLOAK_*` | Keycloak server and realm configuration |
| `EMAIL_*` | SMTP configuration for outgoing mail |
| `HETZNER_API_KEY` | Hetzner Cloud API key for Terraform |
| `PG_CONN_STR` | PostgreSQL connection string for Terraform state backend |