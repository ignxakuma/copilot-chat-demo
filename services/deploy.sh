#!/usr/bin/env bash
# Purpose: Deploy the full platform stack into Kubernetes using Kustomize.
set -euo pipefail

# Apply all manifests including namespace, services, observability, ingress, and HPA.
kubectl apply -k k8s

# Wait for core microservice deployments to become available.
kubectl rollout status deployment/web-frontend -n retail-aiops --timeout=180s
kubectl rollout status deployment/copilot-chat-service -n retail-aiops --timeout=180s
kubectl rollout status deployment/api-gateway -n retail-aiops --timeout=180s
kubectl rollout status deployment/user-service -n retail-aiops --timeout=180s
kubectl rollout status deployment/product-service -n retail-aiops --timeout=180s
kubectl rollout status deployment/order-service -n retail-aiops --timeout=180s
kubectl rollout status deployment/aiops-service -n retail-aiops --timeout=180s
