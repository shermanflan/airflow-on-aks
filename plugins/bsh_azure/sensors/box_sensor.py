from enum import Enum, auto
import logging
import os.path

from airflow.exceptions import AirflowException
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

from bsh_azure.hooks.box_hook import BoxHook

# Quiet chatty libs
logging.getLogger('boxsdk').setLevel(logging.ERROR)


class BoxItemType(Enum):
    FILE = auto()
    FOLDER = auto()


class BoxSensor(BaseSensorOperator):
    # For jinja support, such as:
    # {{ task_instance.xcom_pull(task_ids='foo', key='some_name') }}
    template_fields = ['box_item_path', 'box_item_type']

    @apply_defaults
    def __init__(self,
                 box_item_path,
                 box_item_type=BoxItemType.FILE,
                 box_conn_id='box_default',
                 *args,
                 **kwargs):
        super(BoxSensor, self).__init__(*args, **kwargs)

        self.box_item_path = box_item_path
        self.box_item_type = box_item_type
        self.box_conn_id = box_conn_id
        self._box_hook = None

    def poke(self, context):

        self._box_hook = BoxHook(self.box_conn_id)
        box_root = self._box_hook.get_root()

        if self.box_item_type == BoxItemType.FOLDER:
            self.log.info(f"Checking for folder: {self.box_item_path}")

            folders = self.box_item_path.split('/')
            return self._box_hook.get_folder(box_root, folders) or False

        self.log.info(f"Checking for file: {self.box_item_path}")

        path, file = os.path.split(self.box_item_path)

        if not file:
            raise AirflowException("Invalid path to file")

        folders = path.split('/')[-1::-1]
        parent = self._box_hook.get_folder(box_root, folders)

        return self._box_hook.get_file(parent, file) or False
