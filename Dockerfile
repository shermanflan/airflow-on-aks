FROM apache/airflow:1.10.12

USER root

# ENV APP_HOME /opt/graph_service
# RUN  useradd -ms /bin/bash -r -d ${APP_HOME} graph_service

# For MSSQL ODBC driver
# ENV ACCEPT_EULA=Y
# ENV OS_VERSION=19.10

# RUN buildDeps='curl software-properties-common' \
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
#     && apt-get clean \
#     && apt-get purge -y --auto-remove $buildDeps
#     && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt ${AIRFLOW_HOME}/dev-requirements.txt

RUN pip install --no-cache-dir --user -r ${AIRFLOW_HOME}/dev-requirements.txt \
    && rm /${AIRFLOW_HOME}/dev-requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# COPY --chown=graph_service:graph_service ./graph_api ${APP_HOME}/graph_api
COPY --chown=airflow:airflow ./scripts/airflow-start.sh ${AIRFLOW_HOME}/airflow-start.sh
RUN chmod a+x ${AIRFLOW_HOME}/airflow-start.sh

# WORKDIR ${APP_HOME}
# ENV PATH=$PATH:${APP_HOME}
# ENV PYTHONPATH ${APP_HOME}

CMD ["bash", "./airflow-start.sh"]
