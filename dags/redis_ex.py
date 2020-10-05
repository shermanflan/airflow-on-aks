"""
## redis_ex.py
Example using redis API.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.hooks.redis_hook import RedisHook
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator 
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['shermanflan@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
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


def set_redis(key, value):
    redis_hook = RedisHook(redis_conn_id='redis_default')

    r = redis_hook.get_conn()
    r.set(key, value)


with DAG('redis_ex',
         default_args=default_args,
         description='Example using redis api',
         schedule_interval=timedelta(days=1),
         start_date=days_ago(2),
         tags=['redis']
         ) as dag:

    dag.doc_md = __doc__

    run_this = PythonOperator(
        task_id='Write_Key',
        python_callable=set_redis,
        op_kwargs={
            'key': 'my-airflow:rko',
            'value': f'test {datetime.now()}'
        },
        queue='airworker_q1'
    )

    task2 = BashOperator(
        task_id= 'task_for_q2',
        bash_command='echo $hostname',
        queue='airworker_q2'
    )

    body = """
        Log: <a href="{{ti.log_url}}">Link</a><br>
        Host: {{ti.hostname}}<br>
        Log file: {{ti.log_filepath}}<br>
        Mark success: <a href="{{ti.mark_success_url}}">Link</a><br>
    """

    task3 = EmailOperator(
        task_id= 'email_task',
        to='shermanflan@gmail.com',
        subject='Test from Airflow',
        html_content=body,
        queue='airworker_q2'
    )

    run_this >> task2 >> task3
