#!/bin/bash

# See https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-helm/

# From manifests
# git clone https://github.com/nginxinc/kubernetes-ingress/
# cd kubernetes-ingress/deployments/helm-chart
# git checkout v1.9.0

# cd ~/personal/github-3p/kubernetes-ingress/deployments/helm-chart

echo "Adding the Helm repository"
# helm repo add nginx-stable https://helm.nginx.com/stable
helm repo update

echo "Installing via Helm repository"
helm install ${NGINX_RELEASE} nginx-stable/nginx-ingress

# cd ~/personal/github/airflow-local/

# Uninstall
# helm uninstall ${NGINX_RELEASE}
