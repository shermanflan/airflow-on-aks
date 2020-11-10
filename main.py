import logging
import os
from time import sleep

from cryptography.fernet import Fernet
import redis

log_level_code = getattr(logging, os.environ['LOG_LEVEL'], logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(name)s]: %(message)s'
    , datefmt='%Y-%m-%d %I:%M:%S %p'
    , level=log_level_code)

logger = logging.getLogger(__name__)


def run_pipeline():
    """
    See https://docs.microsoft.com/en-us/python/api/overview/azure/datafactory

    :return:
    """
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.mgmt.datafactory import DataFactoryManagementClient

    subscription_id = os.environ['AZURE_SUBSCRIPTION']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_APP_ID']
        , secret=os.environ['AZURE_APP_KEY']
        , tenant=os.environ['AZURE_TENANT_ID'])
    adf_client = DataFactoryManagementClient(credentials, subscription_id)

    run_response = adf_client.pipelines.create_run(
        resource_group_name='airflow-sandbox'
        , factory_name='bshGeonamestoASDB'
        , pipeline_name='LoadGeographies')

    run = adf_client.pipeline_runs.get(
        resource_group_name='airflow-sandbox'
        , factory_name='bshGeonamestoASDB'
        , run_id=run_response.run_id)

    while run.status not in ('Failed', 'Succeeded'):

        sleep(60)

        run = adf_client.pipeline_runs.get(
            resource_group_name='airflow-sandbox'
            , factory_name='bshGeonamestoASDB'
            , run_id=run_response.run_id)

        logger.info(f"status: {run.status}")
        logger.info(f"start: {run.run_start}")
        logger.info(f"end: {run.run_end}")
        logger.info(f"duration: {run.duration_in_ms}")
        logger.info(f"message: {run.message}")

    return 0


if __name__ == '__main__':

    logger.info('Generate fernet key')
    # fernet_key = Fernet.generate_key()
    # logger.info(f'Fernet: {fernet_key.decode()}')

    logger.info('Connect to redis')
    # r = redis.Redis(host='40.76.155.221', port=6379, db=0)
    # r.set('rko', '21')
    # logger.info(f"RESULT: {r.get('foo')}")

    run_pipeline()