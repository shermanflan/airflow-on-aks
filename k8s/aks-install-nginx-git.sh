#!/bin/bash

# See https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-manifests/
# git clone https://github.com/nginxinc/kubernetes-ingress/
# cd kubernetes-ingress/deployments
# git checkout v1.9.0

cd ~/personal/github-3p/kubernetes-ingress/deployments

echo "Configure RBAC"
kubectl apply -f common/ns-and-sa.yaml
kubectl apply -f rbac/rbac.yaml

echo "Create common resources"
kubectl apply -f common/nginx-config.yaml
kubectl apply -f common/ingress-class.yaml

echo "Create custom Resources"
kubectl apply -f common/vs-definition.yaml
kubectl apply -f common/vsr-definition.yaml
kubectl apply -f common/ts-definition.yaml
kubectl apply -f common/policy-definition.yaml

echo "Deploy the ingress controller"
kubectl apply -f deployment/nginx-ingress.yaml

echo "Create a service for the ingress controller pods"
kubectl apply -f service/loadbalancer.yaml

cd ~/personal/github/airflow-local/

# Uninstall
# kubectl delete namespace nginx-ingress
# kubectl delete clusterrole nginx-ingress
# kubectl delete clusterrolebinding nginx-ingress
