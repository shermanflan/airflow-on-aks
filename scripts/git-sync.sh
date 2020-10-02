#/bin/bash -eux

# TODO: Reset dags folder from git. Should probably be invoked from 
# Dockerfile.
cd ~/personal/github/airflow-local/dags
rm -rf *
rm -rf .git

# sudo apt-get update && sudo apt-get install git
cd ~/personal/github/airflow-local/dags
git clone git@github.com:shermanflan/airflow-dags.git .

# Create crontab schedule.
# crontab -e

# * */5 * * * cd /opt/bitnami/airflow/dags && git pull
cd ~/personal/github/airflow-local
pwd