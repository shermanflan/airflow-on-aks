"""
## redis_q1_ex.py
Example using redis API.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.contrib.hooks.redis_hook import RedisHook
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import (
    BranchPythonOperator, PythonOperator
)
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,  # depends on previous run status
    'email': ['shermanflan@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
    'queue': 'airq1',
    # 'catchup': False
    'pool': 'default_pool',
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
    # 'trigger_rule': 'all_success'  # precedence constraint
}


def branch_func(**context):
    ti = context['ti']
    xcom_value = bool(ti.xcom_pull(task_ids='write_kv',
                                   key='redis-branch-test'))
    if xcom_value:
        return 'print_date'
    else:
        return 'print_date2'


def set_redis(key, value, **context):
    redis_hook = RedisHook(redis_conn_id='redis_default')

    r = redis_hook.get_conn()
    r.set(key, value)

    context['ti'].xcom_push('redis-test', value)
    context['ti'].xcom_push('redis-branch-test', True)


def get_redis(key, **context):
    redis_hook = RedisHook(redis_conn_id='redis_default')

    r = redis_hook.get_conn()
    return r.get(key)


with DAG('redis_q1_ex',
         default_args=default_args,
         description='Example using redis api',
         schedule_interval="@once",
         start_date=days_ago(2),
         tags=['redis']
         ) as dag:

    dag.doc_md = __doc__

    write_kv = PythonOperator(
        task_id='write_kv',
        python_callable=set_redis,
        op_kwargs={
            'key': 'my-airflow:rko',
            'value': f'test21 {datetime.now()}'
        },
        provide_context=True
    )

    task_for_q = BashOperator(
        task_id= 'task_for_q2',
        bash_command='echo $hostname'
    )

    read_kv = PythonOperator(
        task_id='read_kv',
        python_callable=get_redis,
        op_kwargs={
            'key': 'my-airflow:rko',
        },
        provide_context=True
    )

    # Implement conditional branching.
    branch_task = BranchPythonOperator(
        task_id='branch_task',
        provide_context=True,
        python_callable=branch_func)


    print_date = BashOperator(
        task_id='print_date',
        bash_command="echo {{ ts }}"
    )

    print_date2 = BashOperator(
        task_id='print_date2',
        bash_command="echo {{ ts }}"
    )

    # body = """
    #     Log: <a href="{{ti.log_url}}">Link</a><br>
    #     Host: {{ti.hostname}}<br>
    #     Log file: {{ti.log_filepath}}<br>
    #     Mark success: <a href="{{ti.mark_success_url}}">Link</a><br>
    #     Follower branch: {{ ti.xcom_pull(task_ids='write_kv', key='redis-test') }}<br>
    # """

    # email_task_1 = EmailOperator(
    #     task_id= 'email_task_1',
    #     to='shermanflan@gmail.com',
    #     subject="Test from Airflow: {{ ti.xcom_pull(task_ids='write_kv', key='redis-test') }}",
    #     html_content=body,
    #     pool='utility_pool'
    # )

    # email_task_2 = EmailOperator(
    #     task_id= 'email_task_2',
    #     to='shermanflan@gmail.com',
    #     subject="Test from Airflow: {{ ti.xcom_pull(task_ids='write_kv', key='redis-test') }}",
    #     html_content=body,
    #     pool='utility_pool'
    # )

    write_kv >> [task_for_q, read_kv] >> branch_task
    branch_task >> [print_date, print_date2]