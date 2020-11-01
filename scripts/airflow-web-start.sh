#!/bin/bash

echo 'Waiting for database initialization...'

sleep 5

INIT_FILE=$AIRFLOW_HOME/init/.airflowinitialized
if [ ! -f $INIT_FILE ]
  then

    echo 'One-time bootstrapping of Airflow db'
    airflow initdb

    echo 'Updating connnections'
    python "$AIRFLOW_HOME/scripts/airflow-db-init.py"

    echo 'Adding pools'
    airflow pool -s utility_pool 32 "For email, teams, etc."

    touch $INIT_FILE
fi

echo 'Starting Airflow webserver'

airflow webserver &

echo 'Starting Flower UI'

airflow flower --basic_auth=sa:pwd &  # --basic_auth=user1:password1,user2:password2

wait