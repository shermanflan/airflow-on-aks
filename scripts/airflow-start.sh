#/bin/bash

INIT_FILE=.airflowinitialized
if [ ! -f «$INIT_FILE» ]; then
    airflow initdb
fi

# Run the Airflow webserver and scheduler
airflow scheduler &
airflow webserver &
wait