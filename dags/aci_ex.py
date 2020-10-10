"""
## aci_ex.py
Example using Azure operators for ACI.
"""
from datetime import datetime, timedelta
import json
import os

from airflow import DAG
from airflow.contrib.operators.azure_container_instances_operator import (
    AzureContainerInstancesOperator
)
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['shermanflan@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
    'catchup': False
    # 'queue': 'airq1',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

# TODO: Move configuration to variable?
box2lake_path = os.path.join(os.environ['AIRFLOW_HOME'],
                             'dags', 'config', 'box2lake.json')
with open(box2lake_path, 'r') as f:
    box2lake_config = json.load(f)

with DAG('aci_ex',
         default_args=default_args,
         description='Example using Azure ACI operator',
         schedule_interval="0 0 * * *",
         start_date=days_ago(1),
         tags=['azure', 'aci'],
         ) as dag:

    dag.doc_md = __doc__

    start_box_aci = AzureContainerInstancesOperator(
        task_id='start_box_aci',
        ci_conn_id='azure_container_instances_default',
        registry_conn_id='azure_registry_default',
        resource_group='airflow-sandbox',
        name='airflow-dev-box2lake',
        image='x.azurecr.io/y:1.0',
        region='East US',
        environment_variables=box2lake_config,
        memory_in_gb=1.5,
        cpu=1.0,
        queue='airq1',
        pool='default_pool'
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
        subject=f'{start_box_aci.task_id} completed successfully',
        html_content=body,
        queue='airq2',
        pool='utility_pool'
    )

    start_box_aci >> email_task
