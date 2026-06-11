# Kubernetes End-to-End Learning Project

A complete, production-style Kubernetes project built to cover **21 core K8s concepts** hands-on. The app is a **Task Manager** built with microservices: FastAPI backend, Nginx frontend, PostgreSQL database, and Redis cache — all running on Kubernetes.

---

## Architecture

```
                        ┌─────────────┐
                        │   Ingress   │  taskmanager.local
                        └──────┬──────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
       ┌───────▼──────┐               ┌────────▼───────┐
       │   Frontend   │               │    Backend     │
       │  Nginx x2    │               │  FastAPI x2    │
       └──────────────┘               └───────┬────────┘
                                              │
                               ┌──────────────┴──────────────┐
                               │                             │
                      ┌────────▼────────┐           ┌────────▼────────┐
                      │   PostgreSQL    │           │     Redis       │
                      │  (StatefulSet)  │           │  (Deployment)   │
                      └────────┬────────┘           └─────────────────┘
                               │
                      ┌────────▼────────┐
                      │ PersistentVolume│
                      └─────────────────┘
```

---

## Kubernetes Concepts Covered

| # | Concept | File | Purpose |
|---|---------|------|---------|
| 1 | **Namespace** | `k8s/namespace/` | Isolates all project resources |
| 2 | **ConfigMap** | `k8s/configmap/` | Non-sensitive config as env vars |
| 3 | **Secret** | `k8s/secret/` | Sensitive data (DB credentials) |
| 4 | **PersistentVolume** | `k8s/database/pv.yaml` | Physical storage on node |
| 5 | **PersistentVolumeClaim** | `k8s/database/pvc.yaml` | Requests storage from PV |
| 6 | **StatefulSet** | `k8s/database/statefulset.yaml` | Stateful DB with stable identity |
| 7 | **Deployment** | `k8s/backend/`, `k8s/frontend/`, `k8s/redis/` | Manages stateless app replicas |
| 8 | **Service (ClusterIP)** | `k8s/database/service.yaml` | Internal-only communication |
| 9 | **Service (NodePort)** | `k8s/frontend/service.yaml` | Exposes app outside cluster |
| 10 | **Ingress** | `k8s/ingress/` | HTTP routing by host/path |
| 11 | **HorizontalPodAutoscaler** | `k8s/hpa/` | Auto-scales pods on CPU usage |
| 12 | **NetworkPolicy** | `k8s/networkpolicy/` | Restricts pod-to-pod traffic |
| 13 | **Job** | `k8s/jobs/db-seed-job.yaml` | One-time DB seeding task |
| 14 | **CronJob** | `k8s/jobs/backup-cronjob.yaml` | Scheduled daily DB backup |
| 15 | **ServiceAccount** | `k8s/rbac/rbac.yaml` | Pod identity |
| 16 | **Role** | `k8s/rbac/rbac.yaml` | Namespace-scoped permissions |
| 17 | **RoleBinding** | `k8s/rbac/rbac.yaml` | Binds Role to ServiceAccount |
| 18 | **Liveness Probe** | `k8s/backend/deployment.yaml` | Restarts unhealthy pods |
| 19 | **Readiness Probe** | `k8s/backend/deployment.yaml` | Removes unready pods from service |
| 20 | **Startup Probe** | `k8s/backend/deployment.yaml` | Handles slow-starting containers |
| 21 | **Init Container** | `k8s/backend/deployment.yaml` | Waits for DB before app starts |

**Bonus:** Resource Requests & Limits, Rolling Update Strategy, Docker Health Checks

---

## Project Structure

```
catalog/
├── main.py                        # FastAPI backend app
├── requirements.txt
├── Dockerfile                     # Backend Docker image
├── deploy.sh                      # One-command deploy script
├── destroy.sh                     # Cleanup script
├── frontend/
│   ├── index.html                 # Task Manager UI
│   ├── nginx.conf                 # Nginx reverse proxy config
│   └── Dockerfile                 # Frontend Docker image
└── k8s/
    ├── namespace/
    │   └── namespace.yaml
    ├── configmap/
    │   └── configmap.yaml
    ├── secret/
    │   └── secret.yaml
    ├── database/
    │   ├── pv.yaml
    │   ├── pvc.yaml
    │   ├── statefulset.yaml
    │   └── service.yaml
    ├── redis/
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── backend/
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── frontend/
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── ingress/
    │   └── ingress.yaml
    ├── hpa/
    │   └── hpa.yaml
    ├── networkpolicy/
    │   └── networkpolicy.yaml
    ├── jobs/
    │   ├── db-seed-job.yaml
    │   └── backup-cronjob.yaml
    └── rbac/
        └── rbac.yaml
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Frontend | HTML, JavaScript, Nginx |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Container | Docker |
| Orchestration | Kubernetes (Minikube) |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

```bash
# Start Minikube
minikube start --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

---

## Deploy

```bash
# Clone the repo
git clone https://github.com/<your-username>/Kubernetes-end-to-end-learning.git
cd Kubernetes-end-to-end-learning

# Deploy everything with one command
bash deploy.sh
```

The script will:
1. Build Docker images inside Minikube
2. Create namespace
3. Apply ConfigMap & Secret
4. Deploy PostgreSQL (StatefulSet + PV/PVC)
5. Deploy Redis
6. Deploy FastAPI backend
7. Deploy Nginx frontend
8. Apply HPA, NetworkPolicy, Ingress, Jobs

---

## Access the App

```bash
# Open frontend in browser
minikube service frontend-service -n task-manager

# Or port-forward the backend API directly
kubectl port-forward service/backend-service 8000:80 -n task-manager
# Visit: http://localhost:8000/docs  (Swagger UI)
```

---

## Practice Commands

```bash
# View all resources
kubectl get all -n task-manager

# Watch pods in real-time
kubectl get pods -n task-manager -w

# View logs
kubectl logs -f deployment/fastapi-backend -n task-manager

# Exec into a running pod
kubectl exec -it deployment/fastapi-backend -n task-manager -- /bin/sh

# Check HPA (auto-scaler) status
kubectl get hpa -n task-manager

# Manually scale a deployment
kubectl scale deployment fastapi-backend --replicas=4 -n task-manager

# Trigger a rolling update (new image version)
kubectl set image deployment/fastapi-backend fastapi=task-manager-api:v2 -n task-manager

# Rollback to previous version
kubectl rollout undo deployment/fastapi-backend -n task-manager

# View rollout history
kubectl rollout history deployment/fastapi-backend -n task-manager

# Check resource usage (requires metrics-server)
kubectl top pods -n task-manager

# View events for debugging
kubectl get events -n task-manager --sort-by=.metadata.creationTimestamp

# Describe any resource for full details
kubectl describe pod <pod-name> -n task-manager
```

---

## Load Test (Trigger HPA)

```bash
# Generate traffic to watch HPA auto-scale the backend
kubectl run load-test --rm -it --image=busybox -n task-manager -- \
  sh -c "while true; do wget -qO- http://backend-service/tasks; done"

# Watch scaling happen in another terminal
kubectl get hpa -n task-manager -w
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/healthz` | Liveness check |
| GET | `/readyz` | Readiness check |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{id}/done` | Mark task done |
| DELETE | `/tasks/{id}` | Delete a task |

---

## What You Learn

By deploying and exploring this project you get hands-on experience with:

- How **Pods**, **Deployments**, and **StatefulSets** differ and when to use each
- How **Services** route traffic inside and outside the cluster
- How **ConfigMaps** and **Secrets** externalize configuration
- How **PersistentVolumes** keep database data safe across pod restarts
- How **Ingress** acts as a single entry point for HTTP routing
- How **HPA** automatically scales your app under load
- How **NetworkPolicies** secure pod-to-pod communication
- How **Jobs** and **CronJobs** handle batch and scheduled workloads
- How **RBAC** controls what a pod is allowed to do
- How **Health Probes** make Kubernetes self-healing

---

## Cleanup

```bash
bash destroy.sh
```
