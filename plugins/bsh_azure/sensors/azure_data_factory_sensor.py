
from airflow.exceptions import AirflowException
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

from bsh_azure.hooks.azure_data_factory_hook import AzureDataFactoryHook


class AzureDataFactorySensor(BaseSensorOperator):
    # For jinja support, such as:
    # {{ task_instance.xcom_pull(task_ids='foo', key='some_name') }}
    template_fields = ['run_id']

    @apply_defaults
    def __init__(self,
                 resource_group_name,
                 factory_name,
                 run_id,
                 adf_conn_id=None,
                 *args,
                 **kwargs):
        super(AzureDataFactorySensor, self).__init__(*args, **kwargs)

        self.resource_group_name = resource_group_name
        self.factory_name = factory_name
        self.run_id = run_id
        self._adf_hook = None

    def poke(self, context):

        self._adf_hook = AzureDataFactoryHook(self.adf_conn_id)

        run = self._adf_hook.get_pipeline_run(
            resource_group_name=self.resource_group_name
            , factory_name=self.factory_name
            , run_id=self.run_id)

        if run.status == 'Failed':
            raise AirflowException(f"{self.factory_name}: {run.message}.")
        elif run.status == 'Succeeded':
            self.log.info(f"ADF {self.pipeline_name} summary follows.")
            self.log.info(f"Ran from {run.run_start} to {run.run_end}")
            self.log.info(f"Duration: {run.duration_in_ms//1000}s")

            return True

        return False
