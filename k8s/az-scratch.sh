#!/bin/bash

declare RANDOM_PWD=$(openssl rand -base64 8)


# TEST:
# Use ping: kubectl run curl --image=radial/busyboxplus:curl -i --tty

# Registry
#az container create \
#  --resource-group "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --file ~/personal/github/airflow-local/bootstrap/metadata/geonames2lake_test.yaml \
#  --verbose

# ACI
# az container start \
#   -n geonames-containers-qa \
#   --resource-group "$RESOURCE_GROUP" \
#   --subscription "$SUBSCRIPTION" \
#   --verbose --debug

# Tls
# echo "Generating self-signed cert for ${AIRFLOW_HOST}.${DNS_ZONE}"
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#     -keyout ${OUTPUT}/airflow/${KEY_FILE} \
#     -out ${OUTPUT}/airflow/${CERT_FILE} \
#     -subj "/CN=${AIRFLOW_HOST}.${DNS_ZONE}"

# echo "Creating secrets for ${AIRFLOW_HOST}.${DNS_ZONE}"
# kubectl create secret tls ${AIRFLOW_CERT_NAME} \
#     --key ${OUTPUT}/airflow/${KEY_FILE} \
#     --cert ${OUTPUT}/airflow/${CERT_FILE}

# Security
#az role assignment create \
#  --role Owner \
#  --assignee-object-id ae7702dc-ccbe-432d-b343-4fa8e882fee2 \
#  --assignee-principal-type ServicePrincipal \
#  --subscription "aee5590e-06a2-45f1-b3c3-605687cdefab" \
#  --scope "/subscriptions/aee5590e-06a2-45f1-b3c3-605687cdefab"

#az role assignment create \
#  --role Contributor \
#  --assignee-object-id ae7702dc-ccbe-432d-b343-4fa8e882fee2 \
#  --assignee-principal-type ServicePrincipal \
#  --subscription "aee5590e-06a2-45f1-b3c3-605687cdefab" \
#  --scope "/subscriptions/aee5590e-06a2-45f1-b3c3-605687cdefab/resourceGroups/k8s-demo"

# Uninstall cert-manager
# helm --namespace cert-manager delete cert-manager
# kubectl delete namespace cert-manager

# Uninstall nginx
# helm uninstall ${NGINX_RELEASE}