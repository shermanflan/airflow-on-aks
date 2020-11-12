import os
from time import sleep

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from airflow.exceptions import AirflowException

from bsh_azure.hooks.azure_data_factory_hook import AzureDataFactoryHook
from bsh_azure.sensors.azure_data_factory_sensor import AzureDataFactorySensor

POLL_SECONDS = 30


# See https://docs.microsoft.com/en-us/python/api/overview/azure/datafactory
# https://airflow.readthedocs.io/en/1.10.12/plugins.html
class DataFactoryOperator(BaseOperator):
    template_fields = []

    @apply_defaults
    def __init__(self,
                 resource_group_name,
                 factory_name,
                 pipeline_name,
                 adf_conn_id=None,
                 no_wait=False,
                 poll_seconds=30,
                 *args,
                 **kwargs):
        """
        Avoid making any calls out to a service via a hook or any other
        code in the constructor. This will play nice with the Airflow DAG
        scan loop, which invoke operator constructors.

        :param resource_group_name:
        :param factory_name:
        :param pipeline_name:
        :param adf_conn_id:
        :param no_wait:
        :param poll_seconds:
        :param args:
        :param kwargs:
        """
        super(DataFactoryOperator, self).__init__(*args, **kwargs)

        self.resource_group_name = resource_group_name
        self.factory_name = factory_name
        self.pipeline_name = pipeline_name
        self.adf_conn_id = adf_conn_id
        self.no_wait = no_wait
        self._adf_hook = None
        self._adf_sensor = None
        self.poll_seconds = poll_seconds or POLL_SECONDS

    def execute(self, context):

        self.log.info("Getting data factory hook.")

        self._adf_hook = AzureDataFactoryHook(self.adf_conn_id)

        self.log.info("Creating data factory pipeline run.")

        run_response = self._adf_hook.create_run(
            self.resource_group_name,
            self.factory_name,
            self.pipeline_name
        )

        if not self.no_wait:

            while True:

                sleep(self.poll_seconds)

                run = self._adf_hook.get_pipeline_run(
                    self.resource_group_name,
                    self.factory_name,
                    run_response.run_id
                )

                self.log.info(f"status: {run.status}")
                self.log.info(f"start: {run.run_start}")
                self.log.info(f"end: {run.run_end}")
                self.log.info(f"duration: {run.duration_in_ms//1000}")
                self.log.info(f"message: {run.message}")

                if run.status in ('Failed', 'Succeeded'):
                    break

                self.log.info("Polling data factory pipeline run status.")

            if run.status != 'Succeeded':
                raise AirflowException(f"{self.factory_name}: {run.message}.")
