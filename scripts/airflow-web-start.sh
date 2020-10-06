#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

INIT_FILE=.airflowinitialized

if [ ! -f $INIT_FILE ]; then
    echo 'One-time bootstrapping of Airflow db...'

    airflow initdb
#    airflow upgradedb  # recommended for prod

    # Connections
    # TODO: Consider CLI command 'airflow connections'.
    python "$AIRFLOW_HOME/scripts/airflow-db-init.py"

    echo 'Adding pools...'

    airflow pool -s utility_pool 32 "For email, teams, etc."

    touch $INIT_FILE
fi

echo 'Starting Airflow webserver...'

airflow webserver &

wait