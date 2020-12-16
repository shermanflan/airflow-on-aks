import os
from time import sleep

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from bsh_azure.hooks.azure_data_factory_hook import AzureDataFactoryHook
from bsh_azure.sensors.azure_data_factory_sensor import AzureDataFactorySensor

POKE_SECONDS = 30


class DataFactoryOperator(BaseOperator):
    template_fields = []

    @apply_defaults
    def __init__(self,
                 resource_group_name,
                 factory_name,
                 pipeline_name,
                 adf_conn_id=None,
                 no_wait=False,
                 poke_seconds=30,
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
        :type no_wait: bool
        :param poke_seconds:
        :type poke_seconds: int
        """
        super(DataFactoryOperator, self).__init__(*args, **kwargs)

        self.resource_group_name = resource_group_name
        self.factory_name = factory_name
        self.pipeline_name = pipeline_name
        self.adf_conn_id = adf_conn_id
        self.no_wait = no_wait
        self._adf_hook = None
        self.poke_seconds = poke_seconds or POKE_SECONDS

    def execute(self, context):

        self.log.info("Getting data factory hook.")
        self._adf_hook = AzureDataFactoryHook(self.adf_conn_id)

        self.log.info(f"Pull previous task id's return value.")
        run_id_prev = context['ti'].xcom_pull()
        self.log.info(f"Previous run id: {run_id_prev}")

        self.log.info(f"Pull all previous task id's return value.")
        run_id_prevs = context['ti'].xcom_pull(include_prior_dates=True)
        self.log.info(f"All previous run id: {run_id_prevs}")

        self.log.info(f"Creating {self.pipeline_name} pipeline run.")
        run_response = self._adf_hook.create_run(
            self.resource_group_name,
            self.factory_name,
            self.pipeline_name
        )

        self.log.info(f"Current run id: {run_response.run_id}")

        if self.no_wait:
            # TODO: Set XCom with run_id
            # context['ti'].xcom_push('run_id', run_response.run_id)
            return run_response.run_id

        while True:

            self.log.info(f"Polling {self.pipeline_name} run status.")
            sleep(self.poke_seconds)

            run = self._adf_hook.get_pipeline_run(
                self.resource_group_name,
                self.factory_name,
                run_response.run_id
            )

            if run.status in ('Failed', 'Succeeded'):
                break

        if run.status != 'Succeeded':
            raise AirflowException(f"{self.factory_name}: {run.message}.")

        self.log.info(f"ADF {self.pipeline_name} summary follows.")
        self.log.info(f"Ran from {run.run_start} to {run.run_end}")
        self.log.info(f"Duration: {run.duration_in_ms//1000}s")

        return run_response.run_id
