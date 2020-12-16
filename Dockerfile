FROM apache/airflow:1.10.14
#FROM apache/airflow:1.10.12

USER root

# TODO: Load security module w/o git.
#RUN apt-get update \
#    && apt-get install -y git \
#    && apt-get purge -y \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt ${AIRFLOW_HOME}/dev-requirements.txt

RUN pip install --no-cache-dir --user -r ${AIRFLOW_HOME}/dev-requirements.txt \
    && rm /${AIRFLOW_HOME}/dev-requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=airflow:airflow bootstrap/webserver_config.py ${AIRFLOW_HOME}/webserver_config.py
RUN chmod a+x ${AIRFLOW_HOME}/webserver_config.py

COPY --chown=airflow:airflow main.py ${AIRFLOW_HOME}/
COPY --chown=airflow:airflow plugins ${AIRFLOW_HOME}/plugins

# This adds AIRFLOW home to the PYTHONPATH so that modules in the
# dags folder are visible to airflow.
# TODO: Check if this is already in place by base image.
# See: https://medium.com/analytics-and-data/setting-up-airflow-on-azure-connecting-to-ms-sql-server-8c06784a7e2b
# ENV PATH=$PATH:${AIRFLOW_HOME}
# ENV PYTHONPATH=${AIRFLOW_HOME}

CMD ["bash", "./scripts/airflow-all-start.sh"]
