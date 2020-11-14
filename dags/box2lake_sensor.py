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
from airflow.contrib.hooks.redis_hook import RedisHook
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

    body = """
        Log: <a href="{{ti.log_url}}">Link</a><br>
        Host: {{ti.hostname}}<br>
        Log file: {{ti.log_filepath}}<br>
        Mark success: <a href="{{ti.mark_success_url}}">Link</a><br>
    """

    email_task = EmailOperator(
        task_id= 'email_task',
        to='shermanflan@gmail.com',
        subject="Test from Airflow: {{ ti.xcom_pull(task_ids='write_kv', key='redis-test') }}",
        html_content=body,
        pool='utility_pool',
    )

    [wait_for_daily_file, wait_for_weekly_file] >> email_task
