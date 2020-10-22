#!/bin/bash

declare RESOURCE_GROUP='k8s-demo'
declare LOCATION='eastus'
declare K8S_CLUSTER='k8s-poc-1'

# az group create \
#     --name $RESOURCE_GROUP \
#     --location $LOCATION

az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $K8S_CLUSTER 
    --node-count 1
    # --enable-addons monitoring \ 
    # --generate-ssh-keys

# az aks get-credentials \
#     --resource-group $RESOURCE_GROUP \
#     --name $K8S_CLUSTER

az group delete \
    --name $RESOURCE_GROUP
    # --yes --no-wait