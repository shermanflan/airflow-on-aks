#!/bin/bash

STARTTIME=$(date +%s)

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

echo "Publishing ${IMAGE2} to ${REGISTRY}"
docker push $REGISTRY.azurecr.io/${IMAGE2}

echo "Publishing ${IMAGE3} to ${REGISTRY}"
docker push $REGISTRY.azurecr.io/${IMAGE3}

echo "Publishing ${IMAGE4} to ${REGISTRY}"
docker push $REGISTRY.azurecr.io/${IMAGE4}

echo "Publishing ${GEONAMES_IMAGE} to ${REGISTRY}"
docker push $REGISTRY.azurecr.io/$GEONAMES_IMAGE

echo "Publishing ${BOX2ADLS_IMAGE} to ${REGISTRY}"
docker push $REGISTRY.azurecr.io/$BOX2ADLS_IMAGE

# See: https://docs.microsoft.com/en-us/azure/aks/static-ip
# echo "Creating static IP AKSPublicIP"
# az network public-ip create \
#     --resource-group $RESOURCE_GROUP \
#     --name AKSPublicIP \
#     --sku Standard \
#     --allocation-method static

# Disabling RBAC allows the k8s operator to work out of the box.
# See https://github.com/rolanddb/airflow-on-kubernetes#rbac
echo "Creating k8s cluster $K8S_CLUSTER ($K8S_VERSION)"
az aks create \
    --subscription "$SUBSCRIPTION" \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --name $K8S_CLUSTER \
    --node-count 3 \
    --kubernetes-version $K8S_VERSION \
    --load-balancer-sku Standard \
    --outbound-type loadBalancer \
    --network-plugin kubenet \
    --node-vm-size Standard_DS3_v2 \
    --vm-set-type VirtualMachineScaleSets \
    --zones 1 2 3 \
    --no-ssh-key \
    --attach-acr $REGISTRY \
    --enable-addons monitoring \
    --workspace-resource-id "${WORKSPACE_ID}"
    
    # --disable-rbac
    # --debug
    # --dns-name-prefix condesa \
    # --node-osdisk-size 50 \
    # --node-vm-size Standard_B2ms \
    # --node-vm-size Standard_DS2_v2 \
    # --node-vm-size Standard_DS3_v2 \
    # --node-vm-size Standard_D32s_v3 \
    # --node-resource-group $RESOURCE_GROUP_NODES \
    # --enable-cluster-autoscaler \
    # --min-count 3 \
    # --max-count 5 \
    # --cluster-autoscaler-profile scale-down-unready-time=5m \
    # --generate-ssh-keys \
    # --admin-username azureuser \

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

echo "Creating ${INGRESS_NS} namespace"
kubectl create namespace ${INGRESS_NS}

echo "Creating Azure file shares secret for $AKS_PERS_STORAGE_ACCOUNT_NAME"
kubectl create secret generic \
    az-file-secret \
    -n ${INGRESS_NS} \
    --from-literal=azurestorageaccountname=$AKS_PERS_STORAGE_ACCOUNT_NAME \
    --from-literal=azurestorageaccountkey=$STORAGE_KEY

echo "Creating Azure OAuth secrets for tenant $AZURE_TENANT_ID"
kubectl create secret generic \
    az-oauth-secret \
    -n ${INGRESS_NS} \
    --from-literal=azure-tenant-id=$AZURE_TENANT_ID \
    --from-literal=azure-app-id=$AZURE_APP_ID \
    --from-literal=azure-app-key=$AZURE_APP_KEY

# See https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/
# See https://kubernetes.io/docs/concepts/configuration/secret/#using-secrets
echo "Creating Azure auth secret from ${AZURE_CONFIG}"
kubectl create secret generic \
    azure-spn-secret \
    -n ${INGRESS_NS} \
    --from-file=azure-auth=${AZURE_CONFIG}

echo "Creating boxsdk secret from ${BOX_CONFIG}"
kubectl create secret generic \
    box-secret \
    -n ${INGRESS_NS} \
    --from-file=box-auth=${BOX_CONFIG}

# helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
# helm repo add jetstack https://charts.jetstack.io
# echo "Updating Helm repositories"
helm repo update

# See https://docs.microsoft.com/en-us/azure/aks/ingress-tls
echo "Installing k8s' nginx via Helm repository"
helm install ${NGINX_RELEASE} ingress-nginx/ingress-nginx \
    --namespace ${INGRESS_NS} \
    --set controller.replicaCount=1 \
    --set controller.nodeSelector."beta\.kubernetes\.io/os"=linux \
    --set defaultBackend.nodeSelector."beta\.kubernetes\.io/os"=linux \
    --set controller.admissionWebhooks.patch.nodeSelector."beta\.kubernetes\.io/os"=linux

# See https://cert-manager.io/docs/installation/kubernetes/
echo "Installing cert-manager via Helm repository"
helm install \
  cert-manager jetstack/cert-manager \
  --namespace ${INGRESS_NS} \
  --version v1.0.4 \
  --set installCRDs=true \
  --set nodeSelector."beta\.kubernetes\.io/os"=linux

# See https://docs.microsoft.com/en-us/azure/dns/dns-getstarted-cli
# See https://docs.microsoft.com/en-us/azure/dns/dns-zones-records
# See https://docs.microsoft.com/en-us/azure/dns/dns-delegate-domain-azure-dns

# echo "Creating DNS zone ${DNS_ZONE}"
# az network dns zone create \
#     -g ${RESOURCE_GROUP_NODES} \
#     -n ${DNS_ZONE}


declare DNS_ZONE=$(az resource list \
                    --resource-group ${RESOURCE_GROUP_DNS} \
                    --resource-type Microsoft.Network/dnszones \
                    -o json | jq -r '.[0].name')
declare EXTERNAL_IP="$(kubectl get svc ${NGINX_RELEASE}-ingress-nginx-controller \
                        -n ${INGRESS_NS} \
                        -o jsonpath='{..ip}')"

while [ -z ${EXTERNAL_IP} ]
    do

    echo "Waiting for external ip"
    sleep 5

    EXTERNAL_IP="$(kubectl get svc ${NGINX_RELEASE}-ingress-nginx-controller \
                -n ${INGRESS_NS} \
                -o jsonpath='{..ip}')"
done

echo "${NGINX_RELEASE}-ingress-nginx-controller external ip is ${EXTERNAL_IP}"

echo "Updating DNS host record for ${AIRFLOW_HOST}.${DNS_ZONE} on ${EXTERNAL_IP}"
az network dns record-set a delete \
    -n ${AIRFLOW_HOST} \
    -g ${RESOURCE_GROUP_DNS} \
    -z ${DNS_ZONE} \
    --yes

az network dns record-set a add-record \
    -n ${AIRFLOW_HOST} \
    -g ${RESOURCE_GROUP_DNS} \
    -z ${DNS_ZONE} \
    --ttl 60 \
    -a ${EXTERNAL_IP}

echo "Updating DNS host record for ${CELERY_HOST}.${DNS_ZONE} on ${EXTERNAL_IP}"
az network dns record-set a delete \
    -n ${CELERY_HOST} \
    -g ${RESOURCE_GROUP_DNS} \
    -z ${DNS_ZONE} \
    --yes

az network dns record-set a add-record \
    -n ${CELERY_HOST} \
    -g ${RESOURCE_GROUP_DNS} \
    -z ${DNS_ZONE} \
    --ttl 60 \
    -a ${EXTERNAL_IP}

declare ENDTIME=$(date +%s)
echo "Executed script in $(( (${ENDTIME}-${STARTTIME})/60 )) minutes"