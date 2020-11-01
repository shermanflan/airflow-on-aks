#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

echo 'Waiting for database initialization...'

sleep 5

INIT_FILE=$AIRFLOW_HOME/init/.airflowinitialized

if [ ! -f $INIT_FILE ]
  then

    echo 'One-time bootstrapping of Airflow db'

    airflow initdb
#    airflow upgradedb  # recommended for prod

    echo 'Updating connnections'

    python "$AIRFLOW_HOME/scripts/airflow-db-init.py"

    echo 'Adding pools'

    airflow pool -s utility_pool 32 "For email, teams, etc."

#    if [ "$AIRFLOW__WEBSERVER__RBAC" == "True" ]
#      then
#
#        echo 'Adding admin users for RBAC...'
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
