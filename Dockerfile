FROM apache/airflow:1.10.12

USER root

# ENV APP_HOME /opt/graph_service
# RUN  useradd -ms /bin/bash -r -d ${APP_HOME} graph_service

# For MSSQL ODBC driver
# ENV ACCEPT_EULA=Y
# ENV OS_VERSION=19.10

# RUN buildDeps='curl software-properties-common build-essential' \
#     && set -x \
#     && apt-get update \
#     && apt-get install -y $buildDeps \
#     && apt-get update \
#     && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#     && curl https://packages.microsoft.com/config/ubuntu/${OS_VERSION}/prod.list > /etc/apt/sources.list.d/mssql-release.list \
#     && apt-get update \
#     && apt-get install -y \
#         msodbcsql17 \
#         unixodbc-dev \
#         python3-pip \
#     && apt-get purge -y --auto-remove $buildDeps \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt ${AIRFLOW_HOME}/dev-requirements.txt

RUN pip install --no-cache-dir --user -r ${AIRFLOW_HOME}/dev-requirements.txt \
    && rm /${AIRFLOW_HOME}/dev-requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=airflow:airflow scripts/* ${AIRFLOW_HOME}/
RUN chmod a+x ${AIRFLOW_HOME}/*.py
RUN chmod a+x ${AIRFLOW_HOME}/*.sh

CMD ["bash", "./airflow-scheduler-start.sh"]
