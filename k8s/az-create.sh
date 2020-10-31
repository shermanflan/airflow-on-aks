#!/bin/bash

echo "Creating resource group $RESOURCE_GROUP"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

echo "Creating registry ${REGISTRY}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --subscription "$SUBSCRIPTION" \
    --name $REGISTRY \
    --admin-enabled true --sku Basic \
    --verbose

echo "Publishing ${IMAGE} to ${REGISTRY}"
az acr build \
    --registry $REGISTRY \
    --image $IMAGE .

echo "Publishing ${IMAGE2} to ${REGISTRY}"

sed -e '/APP_THEME = "slate/s/^#* //' $WEB_CONFIG
sed -e '/APP_THEME = "cerulean/s/^#*/# /' $WEB_CONFIG

az acr build \
    --registry $REGISTRY \
    --image $IMAGE2 .

sed -e '/APP_THEME = "slate/s/^#*/# /' $WEB_CONFIG
sed -e '/APP_THEME = "cerulean/s/^#* //' $WEB_CONFIG

cd ~/personal/github/azure-methods/Geonames
echo "Publishing ${GEONAMES_IMAGE} to ${REGISTRY}"
az acr build \
    --registry $REGISTRY \
    --image $GEONAMES_IMAGE .
cd ~/personal/github/airflow-local

echo "Creating k8s cluster $K8S_CLUSTER"
az aks create \
    --subscription "$SUBSCRIPTION" \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --name $K8S_CLUSTER \
    --node-count 3 \
    --attach-acr $REGISTRY \
    --dns-name-prefix condesa \
    --kubernetes-version 1.19.0 \
    --load-balancer-sku Standard \
    --outbound-type loadBalancer \
    --network-plugin kubenet \
    --node-osdisk-size 50 \
    --node-vm-size Standard_B2ms \
    --vm-set-type VirtualMachineScaleSets \
    --zones 1 2 3 \
    --no-ssh-key
    # --generate-ssh-keys \
    # --admin-username azureuser \
    # --disable-rbac \
    # --enable-addons monitoring \

# echo "Rescaling cluster $K8S_CLUSTER"
# az aks scale \
#     --resource-group $RESOURCE_GROUP \
#     --name $K8S_CLUSTER \
#     --node-count 4

echo "Getting credentials"
az aks get-credentials \
    --resource-group $RESOURCE_GROUP \
    --name $K8S_CLUSTER \
    --overwrite-existing

echo "Creating Azure file shares secret for $AKS_PERS_STORAGE_ACCOUNT_NAME"
kubectl create secret generic \
    az-file-secret \
    --from-literal=azurestorageaccountname=$AKS_PERS_STORAGE_ACCOUNT_NAME \
    --from-literal=azurestorageaccountkey=$STORAGE_KEY

echo "Creating Azure OAuth secrets for tenant $AZURE_TENANT_ID"
kubectl create secret generic \
    az-oauth-secret \
    --from-literal=azure-tenant-id=$AZURE_TENANT_ID \
    --from-literal=azure-app-id=$AZURE_APP_ID \
    --from-literal=azure-app-key=$AZURE_APP_KEY
