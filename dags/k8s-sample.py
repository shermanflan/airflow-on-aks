

from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'catchup': True,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'queue': 'airq1',
    'pool': 'default_pool',
}

with DAG('kubernetes_sample',
         default_args=default_args,
         start_date=days_ago(2),
         schedule_interval="@daily") as dag:

    passing = KubernetesPodOperator(
        task_id="passing-task",
        name="passing-test",
        namespace='default',
        image="python:3.8-alpine",
        image_pull_policy='Always',
        cmds=["python", "-c"],
        arguments=["print('hello beautiful world at {{ ts }}!')"],
        labels={"app": "hello-world"},
        resources={
            'request_memory': '100Mi', 'request_cpu': '100m',
            'limit_memory': '200Mi', 'limit_cpu': '200m'
        },
        in_cluster=True,
        is_delete_operator_pod=False,
        get_logs=True,
        log_events_on_failure=True
    )
