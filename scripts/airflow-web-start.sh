#!/bin/bash

# Inspired by:
# https://www.cloudwalker.io/2019/09/30/airflow-scale-out-with-redis-and-celery/
# https://www.gradiant.org/en/blog/apache-airflow-docker-en/
# https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

echo 'Waiting for scheduler...'
sleep 30

echo 'Starting Airflow webserver...'

airflow webserver &

echo 'Starting Flower UI...'
airflow flower &

wait