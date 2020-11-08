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

echo "Logging into ${REGISTRY}"
docker login $REGISTRY.azurecr.io \
    -u $REGISTRY \
    -p "$(az acr credential show --name $REGISTRY | jq -r '.passwords[0].value')"

echo "Publishing ${IMAGE} to ${REGISTRY}"
docker push $REGISTRY.azurecr.io/$IMAGE
# az acr build \
#     --registry $REGISTRY \
#     --image $IMAGE .

# echo "Publishing ${IMAGE2} to ${REGISTRY}"
# sed -i -e '/APP_THEME = "cyborg/s/^#* //' $WEB_CONFIG
# sed -i -e '/APP_THEME = "cerulean/s/^#*/# /' $WEB_CONFIG
# az acr build \
#     --registry $REGISTRY \
#     --image $IMAGE2 .
# sed -i -e '/APP_THEME = "cyborg/s/^#*/# /' $WEB_CONFIG
# sed -i -e '/APP_THEME = "cerulean/s/^#* //' $WEB_CONFIG

# echo "Publishing ${GEONAMES_IMAGE} to ${REGISTRY}"
# docker push $REGISTRY.azurecr.io/$GEONAMES_IMAGE

# See: https://docs.microsoft.com/en-us/azure/aks/static-ip
# echo "Creating static IP AKSPublicIP"
# az network public-ip create \
#     --resource-group $RESOURCE_GROUP \
#     --name AKSPublicIP \
#     --sku Standard \
#     --allocation-method static

echo "Creating k8s cluster $K8S_CLUSTER ($K8S_VERSION)"
az aks create \
    --subscription "$SUBSCRIPTION" \
    --resource-group $RESOURCE_GROUP \
    --node-resource-group $RESOURCE_GROUP_NODES \
    --location $LOCATION \
    --name $K8S_CLUSTER \
    --node-count 4 \
    --dns-name-prefix condesa \
    --kubernetes-version $K8S_VERSION \
    --load-balancer-sku Standard \
    --outbound-type loadBalancer \
    --network-plugin kubenet \
    --node-osdisk-size 50 \
    --node-vm-size Standard_B2ms \
    --vm-set-type VirtualMachineScaleSets \
    --zones 1 2 3 \
    --no-ssh-key \
    --attach-acr $REGISTRY \
    --enable-addons http_application_routing,monitoring \
    --workspace-resource-id "${WORKSPACE_ID}"

    # --enable-cluster-autoscaler \
    # --min-count 3 \
    # --max-count 5 \
    # --cluster-autoscaler-profile scale-down-unready-time=5m \
    # --enable-addons http_application_routing,monitoring \
    # --generate-ssh-keys \
    # --admin-username azureuser \
    # --disable-rbac \

# echo "Setting up diagnostic settings for ${K8S_CLUSTER}"
# az monitor diagnostic-settings create \
#         --name auto-monitor \
#         --resource $(az resource list --name ${K8S_CLUSTER} -o json | jq -r '.[0].id') \
#         --logs @${LOG_CONFIG} \
#         --metrics @${METRICS_CONFIG} \
#         --workspace "${WORKSPACE_ID}"

# echo "Creating $SPOT_POOL"
# az aks nodepool add \
#     --resource-group $RESOURCE_GROUP \
#     --cluster-name $K8S_CLUSTER \
#     --name $SPOT_POOL \
#     --priority Spot \
#     --eviction-policy Delete \
#     --spot-max-price -1 \
#     --enable-cluster-autoscaler \
#     --min-count 1 \
#     --max-count 3 \
#     --os-type Linux \
#     --node-vm-size Standard_DS2_v2 \
#     --zones 1 2 3 \
#     --labels poolbudget=spot

# echo "Manually rescaling $K8S_CLUSTER"
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

# Tls
declare DNS_ZONE=$(az resource list --resource-group ${RESOURCE_GROUP_NODES} --resource-type Microsoft.Network/dnszones -o json | jq -r '.[0].name')

echo "Generating self-signed cert for ${AIRFLOW_HOST}.${DNS_ZONE}"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${OUTPUT}/airflow/${KEY_FILE} \
    -out ${OUTPUT}/airflow/${CERT_FILE} \
    -subj "/CN=${AIRFLOW_HOST}.${DNS_ZONE}/O=RKOSelfSigned1"

echo "Creating secrets for ${AIRFLOW_HOST}.${DNS_ZONE}"
kubectl create secret tls ${AIRFLOW_CERT_NAME} \
    --key ${OUTPUT}/airflow/${KEY_FILE} \
    --cert ${OUTPUT}/airflow/${CERT_FILE}

echo "Generating self-signed cert for ${CELERY_HOST}.${DNS_ZONE}"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${OUTPUT}/celery/${KEY_FILE} \
    -out ${OUTPUT}/celery/${CERT_FILE} \
    -subj "/CN=${CELERY_HOST}.${DNS_ZONE}/O=RKOSelfSigned2"

echo "Creating secrets for ${CELERY_HOST}.${DNS_ZONE}"
kubectl create secret tls ${CELERY_CERT_NAME} \
    --key ${OUTPUT}/celery/${KEY_FILE} \
    --cert ${OUTPUT}/celery/${CERT_FILE}
