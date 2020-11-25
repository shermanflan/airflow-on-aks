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
    'queue': 'airq1',
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
         schedule_interval="0 0 * * *",  # "0 0 * * *" or "@daily" or timedelta(hours=2)
         start_date=days_ago(1),
         tags=['azure', 'aks', 'box.com']
         ) as dag:

    dag.doc_md = __doc__

    wait_for_box_daily = BoxSensor(
        task_id='wait_for_daily_box_task',
        box_item_path='Utilization Reports/Daily Schedule Status Reports/2020 Reports/11-November/Branch Scheduled Hours Breakdown_11_15_2020.xlsx',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=300,
        mode='poke'
    )

    wait_for_box_weekly = BoxSensor(
        task_id='wait_for_weekly_box_task',
        box_item_path='Utilization Reports/Weekly Utilization Reports/2020 Reports/11-November/November - 13/Telephony Usage By Branch 11.13.2020.xlsx',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=300,
        mode='poke'
    )

    box2adls_pod_task = KubernetesPodOperator(
        task_id="box2adls_pod_task",
        namespace='airflow-tls',
        service_account_name='airflow-rbac',
        name='boxflow',
        image='rkoH1pVL.azurecr.io/box2adls:latest',
        image_pull_policy='Always',
        labels={'name': 'boxflow', 'instance': 'boxflow-pod',
                'version': '1.0.0', 'component': 'batch-service',
                'part-of': 'pods'},
        env_vars={
            "SIMMER": "False",
            "BROKER_URL": "redis://airflow-redis-service:6379/0",
            "BOX_CONFIG": "/opt/airflow/box-sec/box-auth",
            "BOX_FOLDER_PATH": "Utilization Reports/Daily Schedule Status Reports/2020 Reports/11-November",
            "BOX_FOLDER_PATH2": "Utilization Reports/Weekly Utilization Reports/2020 Reports/11-November/November - 13",
            "BOX_FILE_MASK": "Branch Scheduled Hours Breakdown_11_14_2020.xlsx",
            "BOX_FILE_MASK2": "Telephony Usage By Branch 11.13.2020.xlsx",
            "BOX_FILE_RENAME": "Branch Scheduled Hours Breakdown_af-on-k8s.xlsx",
            "WS_PREV_NAME": "PriorMonth",
            "WS_CURR_NAME": "CurrentMonth",
            "WS_NEXT_NAME": "NextMonth",
            "BOX_FILE_RENAME2": "Telephony Usage By Branch_af-on-k8s.xlsx",
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
            Secret(deploy_type='volume', deploy_target='/opt/airflow/box-sec',
                   secret='box-secret', key=None)
        ],
        resources={
            'request_memory': '200Mi', 'request_cpu': '200m',
            'limit_memory': '2Gi', 'limit_cpu': '2000m'
        },
        in_cluster=True,
        # cluster_context='',
        is_delete_operator_pod=False,
        get_logs=True,
        log_events_on_failure=True
        # config_file='/opt/airflow/dags/config/kube.config',
        # NOTE: this will not work until 1.10.13
        # pod_template_file='/opt/airflow/dags/config/aks-geonames.yaml'
    )

    # body = """
    #     Log: <a href="{{ ti.log_url }}">Link</a><br>
    #     Host: {{ ti.hostname }}<br>
    #     Log file: {{ ti.log_filepath }}<br>
    #     Mark success: <a href="{{ ti.mark_success_url }}">Link</a><br>
    # """
    #
    # email_task = EmailOperator(
    #     task_id= 'email_task',
    #     to='shermanflan@gmail.com',
    #     subject="Test from Airflow: {{ ti.xcom_pull(task_ids='wait_for_box_daily') }}",
    #     html_content=body,
    #     pool='utility_pool',
    # )

    print_date2 = BashOperator(
        task_id='print_date2',
        bash_command="echo {{ ts }}"
    )

    [wait_for_box_daily, wait_for_box_weekly] >> box2adls_pod_task
    box2adls_pod_task >> print_date2
