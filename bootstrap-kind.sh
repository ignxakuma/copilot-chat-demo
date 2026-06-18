#!/usr/bin/env bash
# Purpose: Create and prepare the local Kind cluster with ingress-nginx and metrics-server.
set -euo pipefail

# Create the local Kubernetes cluster using the project Kind config.
kind create cluster --name retail-aiops --config kind/cluster.yaml

# Install metrics-server so HPA can read CPU and memory metrics.
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch metrics-server to trust kubelet certs in local Kind environments.
kubectl patch deployment metrics-server \
  -n kube-system \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# Install ingress-nginx controller for external HTTP routing via Ingress.
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait until the ingress controller is ready before deploying app ingress rules.
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s
