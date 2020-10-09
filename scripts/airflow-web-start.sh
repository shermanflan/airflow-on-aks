#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

INIT_FILE=.airflowinitialized

if [ ! -f $INIT_FILE ]
  then

    echo 'One-time bootstrapping of Airflow db...'

    airflow initdb
#    airflow upgradedb  # recommended for prod

    # Connections
    # TODO: Consider CLI command 'airflow connections'.
    python "$AIRFLOW_HOME/scripts/airflow-db-init.py"

    echo 'Adding pools...'

    airflow pool -s utility_pool 32 "For email, teams, etc."

#    if [ "$AIRFLOW__WEBSERVER__RBAC" == "True" ]
#      then
#
#        echo 'Adding admin user for RBAC...'
#
#        airflow create_user \
#          --role="Admin" \
#          --username="condesa.1931_hotmail.com#EXT#@condesa1931hotmail.onmicrosoft.com" \
#          --email="condesa.1931@hotmail.com" \
#          --firstname="Ricardo" \
#          --lastname="Guzman" \
#          --password="pwd"
#
#        airflow create_user \
#          --role="Admin" \
#          --username="ricardo.guzman@brightspringhealth.com" \
#          --email="ricardo.guzman@brightspringhealth.com" \
#          --firstname="Ricardo" \
#          --lastname="Guzman" \
#          --password="pwd"
#
#    fi

    touch $INIT_FILE
fi

echo 'Starting Airflow webserver...'

airflow webserver &

#echo 'Running the Airflow scheduler...'
#
#airflow scheduler &
#
#echo 'Running workers...'
#
#airflow worker -q airworker_q1,airworker_q2 -cn worker_local --daemon & # 1 worker per host works
#
#echo 'Starting Flower UI...'
#
#airflow flower & # Add --basic_auth=user1:password1,user2:password2"

wait