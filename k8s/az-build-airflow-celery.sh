#!/bin/bash

# kubectl create -f aks-volumes.yaml
# kubectl create -f aks-volume-claims.yaml
# kubectl create -f aks-smtp.yaml
# kubectl create -f aks-postgres.yaml

# kubectl create -f celery/
# kubectl create -f celery/aks-redis.yaml
# kubectl apply -f celery/aks-airflow-web.yaml
kubectl apply -f celery/aks-airflow-scheduler.yaml
kubectl apply -f celery/aks-airflow-workers.yaml
