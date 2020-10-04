#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/

INIT_FILE=.airflowinitialized
if [ ! -f $INIT_FILE ]; then
    echo 'Bootstrapping Airflow...'

    airflow initdb

    python airflow-db-init.py

    touch $INIT_FILE  # run once only
fi

echo 'Run the Airflow webserver and scheduler...'

airflow scheduler &
airflow webserver &

echo 'Run workers...'

airflow worker -q airworker_q1,airworker_q2 --daemon
airflow worker -q airworker_q1,airworker_q2 --daemon
airflow worker -q airworker_q1,airworker_q2 --daemon
airflow worker -q airworker_q1,airworker_q2 --daemon

echo 'Start Flower UI...'
airflow flower &

wait