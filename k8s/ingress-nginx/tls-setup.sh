#!/bin/bash

echo "Creating ${AIRFLOW_HOST} certs/secrets"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${OUTPUT}/airflow/${KEY_FILE} \
    -out ${OUTPUT}/airflow/${CERT_FILE} \
    -subj "/CN=${AIRFLOW_HOST}/O=RKOSelfSigned1"

kubectl create secret tls ${AIRFLOW_CERT_NAME} \
    --key ${OUTPUT}/airflow/${KEY_FILE} \
    --cert ${OUTPUT}/airflow/${CERT_FILE}

echo "Creating ${CELERY_HOST} certs/secrets"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${OUTPUT}/celery/${KEY_FILE} \
    -out ${OUTPUT}/celery/${CERT_FILE} \
    -subj "/CN=${CELERY_HOST}/O=RKOSelfSigned2"

kubectl create secret tls ${CELERY_CERT_NAME} \
    --key ${OUTPUT}/celery/${KEY_FILE} \
    --cert ${OUTPUT}/celery/${CERT_FILE}
