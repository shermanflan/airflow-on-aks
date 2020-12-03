#!/bin/bash

declare K8S_HOME=~/personal/github/airflow-local/k8s
declare EXISTS=$(az storage file exists \
                    --account-name ${AKS_PERS_STORAGE_ACCOUNT_NAME} \
                    --account-key ${STORAGE_KEY} \
                    --path .airflowinitialized \
                    --share-name airflow-init | jq '.exists')

if [ "${EXISTS}" = "true" ]
    then
        echo "Deleting .airflowinitialized"
        az storage file delete \
            --account-name ${AKS_PERS_STORAGE_ACCOUNT_NAME} \
            --account-key ${STORAGE_KEY} \
            --path .airflowinitialized \
            --share-name airflow-init
    else
        echo ".airflowinitialized does not exist"
fi

echo "Creating airflow baseline services"

kubectl create -f ${K8S_HOME}/base/
kubectl create -f ${K8S_HOME}/airflow/

echo "Waiting for airflow services"
sleep 15

echo "Creating airflow"

kubectl apply -f ${K8S_HOME}/airflow/celery/

# echo "Creating certificate issuers and tls ingress"
# kubectl apply -f ${K8S_HOME}/cert-manager/
# kubectl apply -f ${K8S_HOME}/ingress-nginx/aks-airflow-ingress-tls.yaml
