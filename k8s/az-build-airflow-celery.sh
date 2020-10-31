#!/bin/bash

kubectl create -f base/
# kubectl create -f base/aks-smtp.yaml
# kubectl create -f base/aks-volumes.yaml
# kubectl create -f base/aks-volume-claims.yaml

kubectl create -f airflow/celery/
# kubectl create -f airflow/aks-postgres.yaml
# kubectl create -f airflow/celery/aks-redis.yaml
# kubectl apply -f airflow/celery/aks-airflow-web.yaml
# kubectl apply -f airflow/celery/aks-airflow-scheduler.yaml
# kubectl apply -f airflow/celery/aks-airflow-workers.yaml
