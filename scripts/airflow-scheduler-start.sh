#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

echo 'Starting Airflow scheduler'

echo 'Waiting for database initialization...'
sleep 30  # temp hack

echo 'Running the Airflow scheduler...'

airflow scheduler &

# NOTE: Seems like only 1 worker per host works.
# echo 'Running workers...'
# airflow worker -q airq1,airq2 -cn airworker0 --daemon &

# echo 'Starting Flower UI...'
# airflow flower &  # --basic_auth=user1:password1,user2:password2

wait