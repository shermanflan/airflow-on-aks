"""
## redis_q2_ex.py
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
    'queue': 'airworker_q2',
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


def set_redis(key, value, **context):
    redis_hook = RedisHook(redis_conn_id='redis_default')

    r = redis_hook.get_conn()
    r.set(key, value)

    context['ti'].xcom_push('redis-test', value)


def get_redis(key, **context):
    redis_hook = RedisHook(redis_conn_id='redis_default')

    r = redis_hook.get_conn()
    return r.get(key)


with DAG('redis_q2_ex',
         default_args=default_args,
         description='Example using redis api',
         schedule_interval=timedelta(days=1),
         start_date=days_ago(2),
         tags=['redis']
         ) as dag:

    dag.doc_md = __doc__

    write_kv = PythonOperator(
        task_id='write_kv',
        python_callable=set_redis,
        op_kwargs={
            'key': 'my-airflow:rko',
            'value': f'test {datetime.now()}'
        },
        provide_context=True,
        queue='airworker_q2'
    )

    task_for_q = BashOperator(
        task_id= 'task_for_q2',
        bash_command='echo $hostname',
        queue='airworker_q2'
    )

    read_kv = PythonOperator(
        task_id='read_kv',
        python_callable=get_redis,
        op_kwargs={
            'key': 'my-airflow:rko',
        },
        provide_context=True,
        queue='airworker_q2'
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
        queue='airworker_q2'
    )

    write_kv >> [task_for_q, read_kv] >> email_task
