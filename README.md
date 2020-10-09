# airflow-local
Repo for running a local version of airflow for development purposes.

## To Do

- Use git repo sync for dags. 
See [here](https://docs.bitnami.com/azure-templates/infrastructure/apache-airflow/configuration/sync-dags/)
- Use celery executor in a ACI deployment.
    - Mount an Azure files system as a volume for dags and logs.
- Use k8s executor in a AKS deployment.
    - https://airflow.readthedocs.io/en/1.10.12/executor/kubernetes.html
- Use 
[AzureContainerInstanceHook](https://github.com/apache/airflow/blob/v1-10-stable/airflow/contrib/hooks/azure_container_instance_hook.py)
as a reference for implementing an Azure Functions scheduler.
- Implement a Teams operator.
- Add Azure OAuth2.
- Use [`DebugExecutor`](https://airflow.readthedocs.io/en/1.10.12/executor/debug.html) to debug DAG in IDE.
- Consider making all docker compose airflow services 
[homogeneous](https://airflow.readthedocs.io/en/1.10.12/executor/celery.html).
- Consider [plugins](https://airflow.readthedocs.io/en/1.10.12/plugins.html)
as the approach for extending airflow.
- May need to enable [SSL](https://airflow.readthedocs.io/en/1.10.12/security.html#ssl).
- Use .env in docker-compose.yml
- Use [Flask-Mail](https://pypi.org/project/Flask-Mail/) for sending email
in local mode.

## Azure Authentication
This uses a json key file for authentication. To generate:

1. Use az cli to login
2. Run: `ad sp create-for-rbac --sdk-auth > airflow.azureauth`