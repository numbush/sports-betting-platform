# Sports Betting Platform 🏆

> Production-style DevOps patterns on a local Kubernetes lab — from `git push` to staged rollout across two namespaces.

![Kubernetes](https://img.shields.io/badge/Kubernetes-minikube-326CE5)
![Helm](https://img.shields.io/badge/Helm-3-0F1689)
![Jenkins](https://img.shields.io/badge/Jenkins-in--cluster-D24939)
![Docker](https://img.shields.io/badge/Docker-Hub-2496ED)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Local Development](#local-development)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Environments](#environments)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)

---

## Project Overview

A learning-focused sports betting simulation platform (no real money, no real bets). Users can view sports games and odds. Bet placement is available via the API (`POST /bets`), with UI support planned.

The focus is the **full DevOps lifecycle**:

- Building and containerizing a multi-service application
- Deploying to Kubernetes manually, then automating with CI/CD
- Managing multiple environments (dev, staging) with Helm
- Running Jenkins **inside** Kubernetes — demonstrating K8s-native CI/CD with RBAC, PVC persistence, and in-cluster deployments

---

## Architecture

```
User (Browser)
      ↓
Frontend (React + Nginx)
      ↓
Backend API (FastAPI + Python)
      ↓
Database (PostgreSQL)
```

**CI/CD Flow:**
```
Developer pushes code to GitHub
      ↓
Jenkins (Pod in devops-tools namespace)
      ↓
Build Docker images (backend + frontend)
      ↓
Push to Docker Hub (giladkr/*)
      ↓
helm upgrade → sports-betting-dev
      ↓
helm upgrade → sports-betting-staging
      ↓
kubectl rollout status (verify)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Nginx (multi-stage build) |
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL 15 |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (minikube) |
| CI/CD | Jenkins (running inside Kubernetes) |
| Package Management | Helm 3 |
| Container Registry | Docker Hub |
| Infrastructure | Hyper-V VM (Ubuntu 22.04) |

---

## Project Structure

```
sports-betting-platform/
├── frontend/                    # React application
│   ├── src/
│   │   └── App.js
│   ├── Dockerfile               # Multi-stage: Node build → Nginx serve
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── src/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── database/                    # SQL init and seed scripts
│   ├── init.sql
│   └── seed.sql
│
├── k8s/                         # Raw Kubernetes manifests
│   ├── namespaces/
│   ├── frontend/
│   ├── backend/
│   ├── database/
│   ├── ingress/
│   └── jenkins/                 # Jenkins on Kubernetes (custom image)
│       └── Dockerfile           # jenkins/jenkins:lts + Docker + kubectl + Helm
│
├── helm/                        # Helm chart
│   └── sports-betting-platform/
│       ├── Chart.yaml
│       ├── values.yaml          # Default values (dev)
│       ├── values-dev.yaml      # Dev-specific overrides
│       ├── values-staging.yaml  # Staging overrides (2 replicas, 5Gi storage)
│       └── templates/
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── database-statefulset.yaml
│           ├── database-service.yaml
│           ├── database-pvc.yaml
│           ├── db-init-configmap.yaml
│           ├── configmap.yaml
│           └── secret.yaml
│
├── Jenkinsfile                  # CI/CD pipeline definition
└── docker-compose.yaml          # Local development stack
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/games` | GET | List games with odds |
| `/bets` | GET | List placed bets |
| `/bets` | POST | Place a simulated bet |
| `/docs` | GET | Interactive API docs (Swagger) |

---

## Local Development

### Prerequisites

- Docker
- Docker Compose

### Run with Docker Compose

```bash
git clone https://github.com/numbush/sports-betting-platform.git
cd sports-betting-platform
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Kubernetes Deployment

### Prerequisites

- minikube
- kubectl
- Helm 3
- Docker Hub account (for pushing images)

### Start minikube

```bash
minikube start --driver=docker --cpus=2 --memory=3072
```

### Build and load the custom Jenkins image

```bash
docker build -t jenkins-with-docker:v4 k8s/jenkins/
minikube image load jenkins-with-docker:v4
```

### Deploy Jenkins to Kubernetes

```bash
kubectl apply -f k8s/jenkins/namespace.yaml
kubectl apply -f k8s/jenkins/pvc.yaml
kubectl apply -f k8s/jenkins/serviceaccount.yaml
kubectl apply -f k8s/jenkins/rbac.yaml
kubectl apply -f k8s/jenkins/deployment.yaml
kubectl apply -f k8s/jenkins/service.yaml
```

### Jenkins first-time setup

1. Port-forward Jenkins: `kubectl port-forward service/jenkins 8080:8080 -n devops-tools`
2. Get initial password: `kubectl exec -n devops-tools deployment/jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword`
3. Install suggested plugins
4. Create admin user
5. Add Docker Hub credentials: **Manage Jenkins → Credentials → Add** (ID: `dockerhub-credentials`)
6. Create Pipeline job pointing at this repo, branch `giladk`, Jenkinsfile at root

### Deploy the app with Helm

```bash
# Dev environment
helm install sports-betting ./helm/sports-betting-platform \
  --namespace sports-betting-dev \
  --create-namespace

# Staging environment
helm install sports-betting-staging ./helm/sports-betting-platform \
  --namespace sports-betting-staging \
  --create-namespace \
  -f helm/sports-betting-platform/values-staging.yaml
```

### Access the app

Open the frontend — the UI calls the backend via `/api/*` (nginx proxy inside the frontend pod). No backend port-forward is needed for the app to work.

```bash
# Option A: NodePort (recommended)
minikube service frontend -n sports-betting-dev --url
# or: http://$(minikube ip):31050

# Option B: Port-forward frontend only
kubectl port-forward service/frontend 3000:80 -n sports-betting-dev --address 0.0.0.0
```

Optional — direct backend access for Swagger docs only:

```bash
kubectl port-forward service/backend 8000:8000 -n sports-betting-dev --address 0.0.0.0
# API docs: http://localhost:8000/docs
```

| Service | Local Compose | K8s Dev | K8s Staging |
|---------|--------------|---------|-------------|
| Frontend | :3000 | NodePort 31050 | NodePort 31051 |
| Backend API (via UI) | `/api` on :3000 | `/api` on frontend URL | `/api` on frontend URL |
| Backend API (direct) | :8000 | port-forward :8000 (optional) | port-forward :8000 (optional) |
| Jenkins | — | port-forward :8080 | — |

### Useful commands

```bash
# Check all pods
kubectl get pods -n sports-betting-dev
kubectl get pods -n sports-betting-staging

# Check Helm releases
helm list -A

# View deployment history
helm history sports-betting -n sports-betting-dev

# Rollback a release
helm rollback sports-betting 1 -n sports-betting-dev
```

---

## CI/CD Pipeline

Jenkins runs as a Pod inside Kubernetes in the `devops-tools` namespace. This demonstrates K8s-native CI/CD — Jenkins uses its ServiceAccount and RBAC permissions to deploy directly to the cluster without external credentials.

### Pipeline Stages

| Stage | Description |
|-------|-------------|
| Checkout | Pull latest code from GitHub (`giladk` branch) |
| Build Backend Image | Build Docker image for FastAPI backend |
| Build Frontend Image | Multi-stage build: React → Nginx |
| Push to Docker Hub | Push `:BUILD_NUMBER` and `:latest` tags |
| Deploy to Dev | `helm upgrade --install` to `sports-betting-dev` |
| Deploy to Staging | `helm upgrade --install` with `values-staging.yaml` |

### Jenkins Pod Setup

| Component | Purpose |
|-----------|---------|
| PVC (`jenkins-pvc`) | Jobs, credentials, plugins persist across pod restarts |
| Docker socket mount | Build Docker images using host Docker daemon |
| kubectl + Helm in image | Deploy directly to Kubernetes from pipeline |
| RBAC (ClusterRole) | Permission to manage deployments, services, secrets |
| Init container | Fixes file ownership to prevent git safe.directory issues |

---

## Environments

| Environment | Namespace | Backend Replicas | Frontend Replicas | Frontend NodePort |
|-------------|-----------|-----------------|-------------------|-------------------|
| Dev | sports-betting-dev | 1 | 1 | 31050 |
| Staging | sports-betting-staging | 2 | 2 | 31051 |

**Dev** — rapid iteration, minimal resources.  
**Staging** — mirrors production with 2 replicas. Tests load balancing and rolling updates before reaching real users.

---

## Known Limitations

- **Networking**: minikube runs inside Docker on a Hyper-V VM (double-NAT). Access from Windows host requires port-forwarding. In production, use a cloud LoadBalancer or Ingress with a real domain.
- **Database init**: SQL scripts only run on first PVC creation. Deleting the PVC wipes all data.
- **Secrets**: Stored as base64 in Kubernetes Secrets (not encrypted at rest). In production, use External Secrets Operator or HashiCorp Vault.
- **No promotion gate**: Pipeline deploys to staging on every build automatically. In production, add a manual approval step between dev and staging.
- **No automated tests**: Pipeline builds and deploys but doesn't run unit/integration tests yet.
- **Frontend API URL**: Frontend API routing is handled via nginx reverse proxy (/api/* → backend:8000). No backend port-forward needed for the UI.
- **Jenkins image**: Uses `imagePullPolicy: Never` — must be built and loaded into minikube manually on each new cluster.
- **Jenkins RBAC**: Includes NetworkPolicy permissions so Helm can manage them during deploy. In production, network policies should be managed separately by cluster admins, not by CI/CD pipelines.

---

## Future Improvements

- [ ] Add Prometheus + Grafana for monitoring and alerting
- [ ] Implement External Secrets Operator for production-grade secret management
- [ ] Add GitHub webhook for automatic pipeline triggers on push
- [ ] Add unit tests and integration tests to the pipeline
- [ ] Add manual promotion gate between dev and staging
- [ ] Deploy to AWS EKS for production-grade cloud deployment
- [ ] Add Kyverno for policy enforcement
- [ ] Restrict Jenkins RBAC — manage NetworkPolicies outside the CI/CD pipeline
- [ ] Migrate to multi-repo structure (separate repo per service)
- [ ] Add bet placement UI (currently API-only)
- [ ] Add user authentication

---

## Author

**Gilad Krainis**  
[LinkedIn](https://www.linkedin.com/in/gilad-krainis) | [GitHub](https://github.com/numbush)# webhook test
