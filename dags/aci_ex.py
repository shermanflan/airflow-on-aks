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
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator 
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
    # 'queue': 'bash_queue',
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

    run_this = AzureContainerInstancesOperator(
        task_id='Start_Box_ACI',
        queue='airworker_q1',
        ci_conn_id='azure_container_instances_default',
        registry_conn_id='azure_registry_default',
        resource_group='airflow-sandbox',
        name='airflow-dev-box2lake',
        image='bshcontainerregistry.azurecr.io/box2lake:1.0',
        region='East US',
        environment_variables=box2lake_config,
        memory_in_gb=1.5,
        cpu=1.0,
    )

