"""
## geonames_e2e.py
- Example using Azure operators for ADF and AKS.
"""
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.contrib.operators.azure_container_instances_operator import (
    AzureContainerInstancesOperator
)
from airflow.models.variable import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago
# from airflow.utils import timezone

from bsh_azure.operators.azure_data_factory_operator import DataFactoryOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['shermanflan@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
    'queue': 'airq1',
    'pool': 'default_pool',
    # 'priority_weight': 10,
    # 'end_date': timezone.datetime(2016, 1, 1),  # use tz aware
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

# Per Airflow best practices:
# In general, don't write any code outside the tasks. The code outside
# the tasks runs every time Airflow parses the DAG, which happens every
# second by default.
with DAG('geonames_e2e',
         default_args=default_args,
         description='Example using Azure ADF operator',
         schedule_interval="@once",
         start_date=days_ago(1),
         tags=['azure', 'aci'],
         ) as dag:

    dag.doc_md = __doc__

    t1 = BashOperator(
        task_id='print_date',
        bash_command="echo {{var.json.aci_config}}"
    )

    adf_task = DataFactoryOperator(
        task_id='start_geonames_adf',
        resource_group_name='airflow-sandbox',
        factory_name='bshGeonamestoASDB',
        pipeline_name='LoadGeographies',
        # adf_conn_id=None,
        # no_wait=True
    )

    t1 >> adf_task
