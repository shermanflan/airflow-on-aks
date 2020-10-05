# airflow-local
Repo for running a local version of airflow for development purposes.

## To Do

- Use git repo sync for dags. See [here](https://docs.bitnami.com/azure-templates/infrastructure/apache-airflow/configuration/sync-dags/)
- Use k8s executor.
- Use [AzureContainerInstanceHook](https://github.com/apache/airflow/blob/v1-10-stable/airflow/contrib/hooks/azure_container_instance_hook.py)
as a reference for implementing an Azure Functions scheduler.
- Implement a Teams operator.

## Azure Authentication
This uses a json key file for authentication. To generate:

1. Use az cli to login
2. Run: `ad sp create-for-rbac --sdk-auth > airflow.azureauth`