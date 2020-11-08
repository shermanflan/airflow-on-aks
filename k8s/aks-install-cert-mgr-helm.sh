#!/bin/bash

# See https://cert-manager.io/docs/installation/kubernetes/

echo "Creating cert-manager namespace"
kubectl create namespace cert-manager

echo "Adding the Helm repository"
# helm repo add jetstack https://charts.jetstack.io
helm repo update

echo "Installing via Helm repository"
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.0.4 \
  --set installCRDs=true

# Uninstall
# helm --namespace cert-manager delete cert-manager
# kubectl delete namespace cert-manager
# kubectl delete -f https://github.com/jetstack/cert-manager/releases/download/v1.0.4/cert-manager.crds.yaml
