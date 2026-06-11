# Kubernetes End-to-End Project: Task Manager

## Architecture
```
                    [Ingress]
                       |
              +--------+--------+
              |                 |
         [Frontend]       [Backend API]
         (Nginx x2)      (FastAPI x2)
              |                 |
              |         +-------+-------+
              |         |               |
              |    [PostgreSQL]     [Redis]
              |    (StatefulSet)   (Deployment)
              |         |
              |    [PersistentVolume]
```

## K8s Concepts Covered (21 total)

| # | Concept | File | What it does |
|---|---------|------|-------------|
| 1 | **Namespace** | namespace.yaml | Isolates all resources |
| 2 | **ConfigMap** | configmap.yaml | Non-sensitive config as env vars |
| 3 | **Secret** | secret.yaml | Sensitive data (base64 encoded) |
| 4 | **PersistentVolume** | pv.yaml | Physical storage on node |
| 5 | **PersistentVolumeClaim** | pvc.yaml | Request storage from PV |
| 6 | **StatefulSet** | statefulset.yaml | Stateful app (DB) with stable identity |
| 7 | **Service (ClusterIP)** | database/service.yaml | Internal-only service |
| 8 | **Deployment** | redis/deployment.yaml | Stateless app management |
| 9 | **Service (ClusterIP)** | redis/service.yaml | Internal service |
| 10 | **Deployment + InitContainer** | backend/deployment.yaml | App with startup dependency |
| 11 | **Service (ClusterIP)** | backend/service.yaml | Internal service |
| 12 | **Deployment** | frontend/deployment.yaml | Frontend app |
| 13 | **Service (NodePort)** | frontend/service.yaml | External access |
| 14 | **Ingress** | ingress.yaml | HTTP routing rules |
| 15 | **HorizontalPodAutoscaler** | hpa.yaml | Auto-scale on CPU |
| 16 | **NetworkPolicy** | networkpolicy.yaml | Restrict pod-to-pod traffic |
| 17 | **Job** | db-seed-job.yaml | One-time task |
| 18 | **CronJob** | backup-cronjob.yaml | Scheduled task |
| 19 | **ServiceAccount** | rbac.yaml | Pod identity |
| 20 | **Role** | rbac.yaml | Permission rules |
| 21 | **RoleBinding** | rbac.yaml | Bind role to account |

Plus: **Liveness/Readiness/Startup Probes**, **Resource Limits**, **Rolling Updates**, **Health Checks**

## Prerequisites

```bash
# Install minikube & kubectl
minikube start --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

## Deploy

```bash
# One command to deploy everything
bash deploy.sh
```

## Access the App

```bash
# Opens the frontend in your browser
minikube service frontend-service -n task-manager
```

## Useful Commands to Practice

```bash
# See all resources
kubectl get all -n task-manager

# Watch pods in real-time
kubectl get pods -n task-manager -w

# View logs
kubectl logs -f deployment/fastapi-backend -n task-manager

# Exec into a pod
kubectl exec -it deployment/fastapi-backend -n task-manager -- /bin/sh

# Check HPA status
kubectl get hpa -n task-manager

# Describe a resource in detail
kubectl describe pod <pod-name> -n task-manager

# Port forward to access backend directly
kubectl port-forward service/backend-service 8000:80 -n task-manager

# Scale manually
kubectl scale deployment fastapi-backend --replicas=4 -n task-manager

# Rolling update (change image version)
kubectl set image deployment/fastapi-backend fastapi=task-manager-api:v2 -n task-manager

# Rollback
kubectl rollout undo deployment/fastapi-backend -n task-manager

# View rollout history
kubectl rollout history deployment/fastapi-backend -n task-manager

# Check resource usage
kubectl top pods -n task-manager

# View events
kubectl get events -n task-manager --sort-by=.metadata.creationTimestamp
```

## Load Test (trigger HPA)

```bash
# From another terminal, generate load to see auto-scaling
kubectl run load-test --rm -it --image=busybox -n task-manager -- \
  sh -c "while true; do wget -qO- http://backend-service/tasks; done"
```

## Cleanup

```bash
bash destroy.sh
```
