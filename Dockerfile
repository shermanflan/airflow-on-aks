FROM apache/airflow:1.10.12

USER root

# TODO: Load security module w/o git.
RUN apt-get update \
    && apt-get install -y git \
    && apt-get purge -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt ${AIRFLOW_HOME}/dev-requirements.txt

RUN pip install --no-cache-dir --user -r ${AIRFLOW_HOME}/dev-requirements.txt \
    && rm /${AIRFLOW_HOME}/dev-requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=airflow:airflow scripts ${AIRFLOW_HOME}/scripts
RUN chmod a+x ${AIRFLOW_HOME}/scripts/*.py
RUN chmod a+x ${AIRFLOW_HOME}/scripts/*.sh

COPY --chown=airflow:airflow webserver_config.py ${AIRFLOW_HOME}/webserver_config.py
RUN chmod a+x ${AIRFLOW_HOME}/webserver_config.py

CMD ["bash", "./scripts/airflow-web-start.sh"]
