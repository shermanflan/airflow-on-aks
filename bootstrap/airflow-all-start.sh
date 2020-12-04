#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

INIT_FILE=$AIRFLOW_HOME/.airflowinitialized
#INIT_FILE=$AIRFLOW_HOME/init/.airflowinitialized

if [ ! -f $INIT_FILE ]
  then

    echo 'One-time bootstrapping of Airflow db...'

    airflow initdb
#    airflow upgradedb  # recommended for prod

    # Connections
    python "$AIRFLOW_HOME/scripts/airflow-db-init.py"

    echo 'Adding pools...'

    airflow pool -s utility_pool 32 "For email, teams, etc."

  #  if [ "$AIRFLOW__WEBSERVER__RBAC" == "True" ]
  #    then

  #      echo 'Adding admin user for RBAC...'
  #      airflow create_user \
  #        --role="Admin" \
  #        --username="rick.guzman" \
  #        --email="ricardo.guzman@brightspringhealth.com" \
  #        --firstname="Ricardo" \
  #        --lastname="Guzman" \
  #        --password="pwd"

  #  fi

    touch $INIT_FILE
fi

echo 'Starting Airflow webserver...'

airflow webserver &

echo 'Running the Airflow scheduler...'

airflow scheduler &

echo 'Running workers...'

airflow worker -q airq1,airq2 -cn airworker0 --daemon & # 1 worker per host works

echo 'Starting Flower UI...'

airflow flower & # Add --basic_auth=user1:password1,user2:password2"

wait