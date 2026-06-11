#!/bin/bash
# ============================================================
#  TASK MANAGER - End-to-End Kubernetes Deployment Script
# ============================================================
set -e

echo "========================================="
echo "  Task Manager - K8s Deployment"
echo "========================================="

# Step 1: Build Docker images (inside minikube's Docker)
echo "[1/8] Building Docker images..."
eval $(minikube docker-env)
docker build -t task-manager-api:v1 .
docker build -t task-manager-frontend:v1 ./frontend/

# Step 2: Create Namespace
echo "[2/8] Creating namespace..."
kubectl apply -f k8s/namespace/namespace.yaml

# Step 3: Create ConfigMap & Secret
echo "[3/8] Creating ConfigMap & Secret..."
kubectl apply -f k8s/configmap/configmap.yaml
kubectl apply -f k8s/secret/secret.yaml

# Step 4: Deploy Database (PV + PVC + StatefulSet + Service)
echo "[4/8] Deploying PostgreSQL database..."
kubectl apply -f k8s/database/pv.yaml
kubectl apply -f k8s/database/pvc.yaml
kubectl apply -f k8s/database/statefulset.yaml
kubectl apply -f k8s/database/service.yaml

echo "   Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n task-manager --timeout=120s

# Step 5: Deploy Redis
echo "[5/8] Deploying Redis cache..."
kubectl apply -f k8s/redis/deployment.yaml
kubectl apply -f k8s/redis/service.yaml

kubectl wait --for=condition=ready pod -l app=redis -n task-manager --timeout=60s

# Step 6: Deploy Backend
echo "[6/8] Deploying FastAPI backend..."
kubectl apply -f k8s/rbac/rbac.yaml
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml

kubectl wait --for=condition=ready pod -l app=fastapi-backend -n task-manager --timeout=120s

# Step 7: Deploy Frontend
echo "[7/8] Deploying Nginx frontend..."
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml

# Step 8: Apply HPA, NetworkPolicy, Ingress, Jobs
echo "[8/8] Applying HPA, NetworkPolicy, Ingress..."
kubectl apply -f k8s/hpa/hpa.yaml
kubectl apply -f k8s/networkpolicy/networkpolicy.yaml
kubectl apply -f k8s/ingress/ingress.yaml || echo "   (Ingress skipped - enable with: minikube addons enable ingress)"

# Seed the database
echo ""
echo "Seeding database with sample tasks..."
kubectl apply -f k8s/jobs/db-seed-job.yaml
kubectl apply -f k8s/jobs/backup-cronjob.yaml

echo ""
echo "========================================="
echo "  Deployment Complete!"
echo "========================================="
echo ""
echo "Access the app:"
echo "  minikube service frontend-service -n task-manager"
echo ""
echo "Useful commands:"
echo "  kubectl get all -n task-manager"
echo "  kubectl logs -f deployment/fastapi-backend -n task-manager"
echo "  kubectl top pods -n task-manager"
echo "  kubectl describe hpa backend-hpa -n task-manager"
