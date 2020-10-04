#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

INIT_FILE=.airflowinitialized

if [ ! -f $INIT_FILE ]; then
    echo 'Bootstrapping Airflow db...'

    airflow initdb

    python $AIRFLOW_HOME/scripts/airflow-db-init.py

    touch $INIT_FILE  # run once only
fi

echo 'Running the Airflow scheduler...'

airflow scheduler &

echo 'Run workers...'

airflow worker -q airworker_q1,airworker_q2 --daemon
airflow worker -q airworker_q1,airworker_q2 --daemon
airflow worker -q airworker_q1,airworker_q2 --daemon
airflow worker -q airworker_q1,airworker_q2 --daemon

wait