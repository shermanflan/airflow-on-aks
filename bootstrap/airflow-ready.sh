#!/bin/bash

# Alternatively: curl -s --connect-timeout 5 http://20.62.208.15:8080/health | grep healthy | wc -l
declare airflow_status="$(curl -s --connect-timeout 5 http://20.62.208.16:8080/health | jq -r .metadatabase.status)"

echo "Airflow is ${airflow_status}"

while [ "$airflow_status" != "healthy" ]
    do

    echo "Airflow is ${airflow_status} != healthy"

    sleep 5

    airflow_status="$(curl -s http://20.62.208.15:8080/health | jq -r .metadatabase.status)"

done

echo "Airflow is now ${airflow_status}"