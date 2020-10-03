#/bin/bash

INIT_FILE=.airflowinitialized
if [ ! -f $INIT_FILE ]; then
    airflow initdb
    
    # Bootstrap Airflow
    python airflow-init.py
    
    # This configuration is done only the first time
    touch $INIT_FILE
fi

# Run the Airflow webserver and scheduler
airflow scheduler &
airflow webserver &

# Workers
airflow worker -q cloudwalker_q1,cloudwalker_q2 --daemon
airflow worker -q cloudwalker_q1,cloudwalker_q2 --daemon
airflow worker -q cloudwalker_q1,cloudwalker_q2 --daemon
airflow worker -q cloudwalker_q1,cloudwalker_q2 --daemon

# Flower UI
airflow flower &

wait