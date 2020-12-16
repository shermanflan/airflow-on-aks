"""
## geonames_e2e.py
Example using Box.com sensors along with Azure operators for ADF and AKS.

- Code inspired by [contrib repo](https://github.com/apache/airflow/tree/1.10.12/airflow/contrib).
"""
from datetime import timedelta

from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import (
    KubernetesPodOperator
)
from airflow.kubernetes.secret import Secret
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago

from bsh_azure.operators.azure_data_factory_operator import (
    DataFactoryOperator
)
from bsh_azure.sensors.box_sensor import BoxSensor, BoxItemType

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['shermanflan@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
    # 'retry_exponential_backoff': True,
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
         tags=['azure', 'aks', 'adf', 'demo'],
         # Cron presets
         # '@once': None
         # '@hourly': '0 * * * *'
         # '@daily': '0 0 * * *'
         # '@weekly': '0 0 * * 0'
         # '@monthly': '0 0 1 * *'
         # '@quarterly': '0 0 1 */3 *'
         # '@yearly': '0 0 1 1 *'
         schedule_interval="@daily",
         start_date=days_ago(3),
         catchup=False
         ) as dag:

    dag.doc_md = __doc__

    wait_for_box_daily = BoxSensor(
        task_id='wait_for_daily_box_task',
        box_item_path='data_source_01/folder_1/2020/20-August/PastaBologneseRecipe.pdf',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=600,
        mode='poke'
    )

    wait_for_box_weekly = BoxSensor(
        task_id='wait_for_weekly_box_task',
        box_item_path='data_source_01/folder_1/2020/20-August/BeefStewRecipe.pdf',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=300,
        mode='poke'
    )

    wait_for_box_monthly = BoxSensor(
        task_id='wait_for_monthly_box_task',
        box_item_path='data_source_01/folder_1/2020/20-August/Split_RoastedChicken.pdf',
        box_item_type=BoxItemType.FILE,
        poke_interval=5,
        timeout=300,
        mode='poke'
    )

    geonames_pod_task = KubernetesPodOperator(
        task_id="geonames_pod_task",
        namespace='airflow-tls',
        service_account_name='airflow-rbac',
        name='geoflow',
        image='rkoH1pVL.azurecr.io/geonames:latest',
        image_pull_policy='Always',
        labels={'name': 'geoflow', 'instance': 'geoflow-pod',
                'version': '1.0.0', 'component': 'batch-service',
                'part-of': 'pods'},
        env_vars={'APP_LOG_KEY': 'rko.aks.geonames2lake.dev',
                  'LOG_LEVEL': 'DEBUG',
                  'ON_QUEUE': 'False',
                  'CENSUS_STATES_URI': 'https://www2.census.gov/programs-surveys/popest/geographies/2019/state-geocodes-v2019.xlsx',
                  'CENSUS_COUNTIES_URI': 'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/2019_Gaz_counties_national.zip',
                  'GEONAMES_ZIPCODES_URI': 'http://download.geonames.org/export/zip/US.zip',
                  'CENSUS_STATE_NAME': 'MasterData.StateTerritory',
                  'CENSUS_COUNTY_NAME': 'MasterData.CountyProvince',
                  'GEONAMES_ZIPCODE_NAME': 'MasterData.ZipCode',
                  'LAKE_ACCOUNT_NAME': 'airflowstoragesandbox',
                  'LAKE_CONTAINER_NAME': 'enterprisedata',
                  'LAKE_BASE_PATH': 'Raw/Master Data/Geography/Brightspring',
                  },
        secrets=[
            Secret(deploy_type='env', deploy_target='LAKE_ACCOUNT_KEY',
                   secret='az-file-secret', key='azurestorageaccountkey')
        ],
        resources={
            'request_memory': '250Mi', 'request_cpu': '200m',
            'limit_memory': '1Gi', 'limit_cpu': '1000m'
        },
        in_cluster=True,
        is_delete_operator_pod=True,
        get_logs=True,
        log_events_on_failure=True
    )

    geonames_adf_task = DataFactoryOperator(
        task_id='geonames_adf_task',
        resource_group_name='airflow-sandbox',
        factory_name='GeonamesADLStoASDB',
        pipeline_name='MasterEntrypoint',
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
    #     subject="Test from Airflow: {{ ti.xcom_pull(task_ids='print_date') }}",
    #     html_content=body,
    #     pool='utility_pool',
    # )

    # print_date >> geonames_pod_task >> print_date2
    # print_date >> geonames_pod_task >> geonames_adf_task >> print_date2
    [wait_for_box_daily, wait_for_box_weekly, wait_for_box_monthly] >> geonames_pod_task
    geonames_pod_task >> geonames_adf_task
