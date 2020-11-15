"""
## box2lake_sensor.py
Example using Box.com API.

- Demonstrates a Box sensor for file availability before proceeding with ETL.

### References
Box APIs used

- REST: https://developer.box.com/reference/
- Python SDK: https://box-python-sdk.readthedocs.io/en/stable/boxsdk.html
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import (
    KubernetesPodOperator
)
from airflow.kubernetes.secret import Secret
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator 
from airflow.utils.dates import days_ago

from bsh_azure.sensors.box_sensor import BoxSensor, BoxItemType

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['shermanflan@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(seconds=5),
    'queue': 'airq2',
    'catchup': False,
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(minutes=30),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}


with DAG('box2lake_sensor',
         default_args=default_args,
         description='Example using Box.com api',
         schedule_interval=None,  # "0 0 * * *" or "@daily" or timedelta(hours=2)
         start_date=days_ago(1),
         tags=['azure', 'aks', 'box.com']
         ) as dag:

    dag.doc_md = __doc__

    wait_for_daily_file = BoxSensor(
        task_id='wait_for_daily_file_task',
        box_item_path='Utilization Reports/Daily Schedule Status Reports/2020 Reports/11-November/Branch Scheduled Hours Breakdown_11_15_2020.xlsx',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=300,
        mode='poke'
    )

    wait_for_weekly_file = BoxSensor(
        task_id='wait_for_weekly_file_task',
        box_item_path='Utilization Reports/Weekly Utilization Reports/2020 Reports/11-November/November - 13/Telephony Usage By Branch 11.13.2020.xlsx',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=300,
        mode='poke'
    )

    box2adls_pod_task = KubernetesPodOperator(
        task_id="box2adls_pod_task",
        namespace='airflow-tls',
        name='boxflow',
        image='rkoH1pVL.azurecr.io/box2adls:latest',
        image_pull_policy='Always',
        labels={'name': 'boxflow', 'instance': 'boxflow-pod',
                'version': '1.0.0', 'component': 'batch-service',
                'part-of': 'pods'},
        env_vars={
            "SIMMER": "True",
            "BROKER_URL": "redis://redis-kv:6379/0",
            "BOX_FOLDER_PATH": "Utilization Reports/Daily Schedule Status Reports/2020 Reports",
            "BOX_FOLDER_PATH2": "Utilization Reports/Weekly Utilization Reports/{0} Reports",
            "BOX_FILE_MASK": "Branch Scheduled Hours Breakdown_{0}.xlsx",
            "BOX_FILE_MASK2": "Telephony Usage By Branch {0}.xlsx",
            "BOX_FILE_RENAME": "Branch Scheduled Hours Breakdown.xlsx",
            "WS_PREV_NAME": "PriorMonth",
            "WS_CURR_NAME": "CurrentMonth",
            "WS_NEXT_NAME": "NextMonth",
            "BOX_FILE_RENAME2": "Telephony Usage By Branch.xlsx",
            "WS_HIDDEN_NAME": "{0} Tele Stats",
            "WS_HIDDEN_RENAME": "Tele Stats",
            "LAKE_ACCOUNT_NAME": "airflowstoragesandbox",
            # "LAKE_ACCOUNT_KEY": "",
            "LAKE_CONTAINER_NAME": "enterprisedata",
            "LAKE_FOLDER_PATH": "Raw/BOX Reports"
        },
        secrets=[
            Secret(deploy_type='env', deploy_target='LAKE_ACCOUNT_KEY',
                   secret='az-file-secret', key='azurestorageaccountkey'),
            Secret(deploy_type='env', deploy_target='BOX_CONFIG',
                   secret='az-file-secret', key='azurestorageaccountkey')
        ],
        resources={
            'request_memory': '500Mi', 'request_cpu': '500m',
            'limit_memory': '2Gi', 'limit_cpu': '2000m'
        },
        # is_delete_operator_pod=True,
        in_cluster=False,
        # cluster_context='',
        get_logs=True,
        config_file='/opt/airflow/dags/config/kube.config',
        # NOTE: this will not work until 1.10.13
        # pod_template_file='/opt/airflow/dags/config/aks-geonames.yaml'
    )

    body = """
        Log: <a href="{{ti.log_url}}">Link</a><br>
        Host: {{ti.hostname}}<br>
        Log file: {{ti.log_filepath}}<br>
        Mark success: <a href="{{ti.mark_success_url}}">Link</a><br>
    """

    email_task = EmailOperator(
        task_id= 'email_task',
        to='shermanflan@gmail.com',
        subject="Test from Airflow: {{ ti.xcom_pull(task_ids='wait_for_daily_file_task') }}",
        html_content=body,
        pool='utility_pool',
    )

    [wait_for_daily_file, wait_for_weekly_file] >> email_task
