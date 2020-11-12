
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

from bsh_azure.hooks.azure_data_factory_hook import AzureDataFactoryHook


class AzureDataFactorySensor(BaseSensorOperator):

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

        self.log.info("Polling data factory pipeline run status.")
        self.log.info(f"status: {run.status}")
        self.log.info(f"start: {run.run_start}")
        self.log.info(f"end: {run.run_end}")
        self.log.info(f"duration: {run.duration_in_ms // 1000}")
        self.log.info(f"message: {run.message}")

        return run.status in ('Failed', 'Succeeded')
