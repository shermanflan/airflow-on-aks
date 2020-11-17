import os

from airflow.exceptions import AirflowException
from airflow.hooks.base_hook import BaseHook

from azure.common.client_factory import get_client_from_auth_file
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.datafactory import DataFactoryManagementClient


# There are no required methods that BaseHook-derived hook must
# implement.
class AzureDataFactoryHook(BaseHook):
    """
    Interact with Azure Data Factory.

    References:
    - https://docs.microsoft.com/en-us/python/api/overview/azure/datafactory
    - https://github.com/apache/airflow/blob/v1-10-stable/airflow/contrib/hooks/azure_cosmos_hook.py#L50
    """

    def __init__(self, conn_id='azure_data_factory_default'):
        """
        If using service principal authentication, then the Connection
        login should be the application id and password should be the
        secret. Use the following extras:
        {"tenantId": "tenant", "subscriptionId": "subscription"}.

        Alternatively, if using a JSON key file, there are 2 options:

        1. Set the file path in environment variable AZURE_AUTH_LOCATION
        2. Use the following extras: {"key_path": "path to file"}

        :param conn_id:
        """
        self.conn_id = conn_id
        self._adf_client = None

    def get_conn(self):
        """
        :return:
        """
        if self._adf_client:
            return self._adf_client

        key_path = os.environ.get('AZURE_AUTH_LOCATION', False)

        if not key_path:
            conn = self.get_connection(self.conn_id)
            key_path = conn.extra_dejson.get('key_path', False)

        if key_path:
            self.log.info('Getting connection using a JSON key file.')
            self._adf_client = get_client_from_auth_file(
                DataFactoryManagementClient, key_path
            )
            return self._adf_client

        self.log.info('Getting connection using a service principal.')
        credentials = ServicePrincipalCredentials(
            client_id=conn.login,
            secret=conn.password,
            tenant=conn.extra_dejson['tenantId']
        )

        self._adf_client = DataFactoryManagementClient(
            credentials, conn.extra_dejson['subscriptionId']
        )
        return self._adf_client

    def create_run(self, resource_group_name, factory_name, pipeline_name):
        return self.get_conn().pipelines.create_run(
            resource_group_name=resource_group_name
            , factory_name=factory_name
            , pipeline_name=pipeline_name
        )

    def get_pipeline_run(self, resource_group_name, factory_name, run_id):
        return self.get_conn().pipeline_runs.get(
            resource_group_name=resource_group_name
            , factory_name=factory_name
            , run_id=run_id
        )

