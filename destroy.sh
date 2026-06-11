#!/bin/bash
# Tear down the entire project
echo "Destroying all resources in task-manager namespace..."
kubectl delete namespace task-manager
kubectl delete pv postgres-pv
echo "Done! All resources cleaned up."
