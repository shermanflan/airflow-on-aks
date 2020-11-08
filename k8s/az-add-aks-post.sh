#!/bin/bash

# See https://docs.microsoft.com/en-us/azure/dns/dns-getstarted-cli
# declare DNS_ZONE=condesa1931.com
declare DNS_ZONE=$(az resource list --resource-group ${RESOURCE_GROUP_NODES} --resource-type Microsoft.Network/dnszones -o json | jq -r '.[0].name')
declare EXTERNAL_IP=$(kubectl get svc ${NGINX_RELEASE}-nginx-ingress -o jsonpath='{..ip}')  # helm
# declare EXTERNAL_IP=$(kubectl get svc nginx-ingress -n nginx-ingress -o jsonpath='{..ip}')  # manifests

# echo "Creating DNS zone ${DNS_ZONE}"
# az network dns zone create \
#     -g ${RESOURCE_GROUP_NODES} \
#     -n ${DNS_ZONE}

# echo "Creating DNS host record for ${AIRFLOW_HOST}.${DNS_ZONE} on ${EXTERNAL_IP}"
# az network dns record-set a add-record \
#     -g ${RESOURCE_GROUP_NODES} \
#     -z ${DNS_ZONE} \
#     -n ${AIRFLOW_HOST} \
#     -a ${EXTERNAL_IP}

# echo "Creating DNS host record for ${CELERY_HOST}.${DNS_ZONE} on ${EXTERNAL_IP}"
# az network dns record-set a add-record \
#     -g ${RESOURCE_GROUP_NODES} \
#     -z ${DNS_ZONE} \
#     -n ${CELERY_HOST} \
#     -a ${EXTERNAL_IP}

echo "Generating self-signed cert for ${CELERY_HOST}.${DNS_ZONE}"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${OUTPUT}/celery/${KEY_FILE} \
    -out ${OUTPUT}/celery/${CERT_FILE} \
    -subj "/CN=${CELERY_HOST}.${DNS_ZONE}"

echo "Creating secrets for ${CELERY_HOST}.${DNS_ZONE}"
kubectl create secret tls quickstart-example-tls \
    --key ${OUTPUT}/celery/${KEY_FILE} \
    --cert ${OUTPUT}/celery/${CERT_FILE}

# echo "Listing DNS records for ${DNS_ZONE}"
# az network dns record-set list \
#     -g ${RESOURCE_GROUP_NODES} \
#     -z ${DNS_ZONE}

# echo "Listing names server for ${DNS_ZONE}"
# az network dns record-set ns show \
#     --resource-group ${RESOURCE_GROUP_NODES} \
#     --zone-name ${DNS_ZONE} \
#     --name @

# Test
# nslookup ${DNS_ZONE} ns4-06.azure-dns.info.
