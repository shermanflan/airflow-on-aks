import os

from airflow.exceptions import AirflowException
from airflow.hooks.base_hook import BaseHook

from azure.common.client_factory import get_client_from_auth_file
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.datafactory import DataFactoryManagementClient


class AzureDataFactoryHook(BaseHook):
    """
    There are no required methods that BaseHook-derived hook must
    implement.
    """

    def __init__(self, conn_id='azure_data_factory_default'):
        self.conn_id = conn_id
        self.connection = self.get_conn()

    def get_conn(self):

        if os.environ.get('AZURE_AUTH_LOCATION'):
            key_path = os.environ.get('AZURE_AUTH_LOCATION')
            if key_path.endswith('.json'):
                self.log.info('Getting connection using a JSON key file.')
                return get_client_from_auth_file(DataFactoryManagementClient,
                                                 key_path)
            else:
                raise AirflowException('Unrecognised extension for key file.')

        conn = self.get_connection(self.conn_id)
        key_path = conn.extra_dejson.get('key_path', False)
        if key_path:
            if key_path.endswith('.json'):
                self.log.info('Getting connection using a JSON key file.')
                return get_client_from_auth_file(DataFactoryManagementClient,
                                                 key_path)
            else:
                raise AirflowException('Unrecognised extension for key file.')

        credentials = ServicePrincipalCredentials(
            client_id=conn.login,
            secret=conn.password,
            tenant=conn.extra_dejson['tenantId']
        )

        subscription_id = conn.extra_dejson['subscriptionId']
        return DataFactoryManagementClient(credentials, str(subscription_id))

    def create_run(self, resource_group_name, factory_name, pipeline_name):
        return self.connection.pipelines.create_run(
            resource_group_name=resource_group_name
            , factory_name=factory_name
            , pipeline_name=pipeline_name
        )

    def get_pipeline_run(self, resource_group_name, factory_name, run_id):
        return self.connection.pipeline_runs.get(
            resource_group_name=resource_group_name
            , factory_name=factory_name
            , run_id=run_id
        )

