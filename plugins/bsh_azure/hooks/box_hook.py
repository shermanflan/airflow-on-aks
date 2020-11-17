"""
There are no required methods that BaseHook-derived hook must
implement.
"""
import logging
import os

from airflow.exceptions import AirflowException
from airflow.hooks.base_hook import BaseHook

from boxsdk import JWTAuth, Client

# Quiet chatty libs
logging.getLogger('boxsdk').setLevel(logging.ERROR)


class BoxHook(BaseHook):
    """
    Interact with Box.com.

    References:
    - https://developer.box.com/reference/
    - https://box-python-sdk.readthedocs.io/en/stable/boxsdk.html
    """

    def __init__(self, conn_id='box_default'):
        """
        Authentication using a JSON key file is supported:

        1. Set the file path in environment variable BOX_AUTH_LOCATION

        TODO:
        - Add client token option passed in through 'box_default'

        :param conn_id:
        """
        self.conn_id = conn_id
        self._box_client = None

    def get_conn(self):
        """
        :return:
        """
        if self._box_client:
            return self._box_client

        key_path = os.environ.get('BOX_AUTH_LOCATION', False)

        if key_path:
            self.log.info('Getting connection using a JSON key file.')
            self._box_client = Client(JWTAuth.from_settings_file(key_path))
            return self._box_client
        else:
            raise AirflowException("BOX JSON key file is missing")

    def get_root(self):
        return self.get_conn().folder('0').get()

    def get_folder(self, box_folder, folders):
        """
        Navigates through a path list and returns the last folder in the path.

        :param box_folder: the starting box folder
        :param folders: the folder path to navigate
        :type folders: List
        :return: Last folder in the given path or None if not found
        :type [boxsdk.object.folder](https://box-python-sdk.readthedocs.io)
        """
        if not folders:
            return box_folder

        current_folder = folders.pop()

        items = box_folder.get_items()

        for i in items:

            if i.type == 'folder' and i.name == current_folder:
                self.log.debug(f'Box Folder: "{i.name}" ({i.id})')
                return self.get_folder(i, folders)

        return None

    def get_file(self, box_folder, file_name):
        """
        Get file in given box directory.

        :param box_folder: the source folder in Box
        :type [boxsdk.object.folder](https://box-python-sdk.readthedocs.io)
        :param file_name: file name filter
        :return: File or None if not found
        :type [boxsdk.object.file](https://box-python-sdk.readthedocs.io)
        """
        items = box_folder.get_items()

        for i in items:

            self.log.debug(f'Comparing "{i.name}" and "{file_name}"')

            if i.type == 'file' and i.name == file_name:

                self.log.info(f'Found Box file: "{file_name}"')
                return i

        return None
