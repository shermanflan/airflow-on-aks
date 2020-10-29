#!/bin/bash

kubectl create -f aks-volumes.yaml
kubectl create -f aks-volume-claims.yaml
kubectl create -f aks-smtp.yaml
kubectl create -f aks-redis.yaml
kubectl create -f aks-postgres.yaml
kubectl create -f aks-airflow-web.yaml
kubectl create -f aks-airflow-scheduler.yaml
kubectl create -f aks-airflow-workers.yaml
