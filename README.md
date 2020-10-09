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
- Use [`DebugExecutor`](https://airflow.readthedocs.io/en/1.10.12/executor/debug.html) to debug DAG in IDE.
- Consider [plugins](https://airflow.readthedocs.io/en/1.10.12/plugins.html)
as the approach for extending airflow.
- May need to enable [SSL](https://airflow.readthedocs.io/en/1.10.12/security.html#ssl).
- Use [Flask-Mail](https://pypi.org/project/Flask-Mail/) for sending email
in local mode.

## Azure Authentication for Web UI
This is based on OAuth2 authorization code flow facilitated by 
Flask-AppBuilder. In order for the OAuth2 flow to work, a application
registration is required with the following properties.

- API permissions: User.Read (Delegated)
- Redirect URIs should include (port is ignored by Azure):
    - http://[your airflow URI]/oauth-authorized/azure

Per Microsoft [guidelines](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow), 
the following should be kept in mind.

- Redirect URI may need to be https for non-localhost URIs
- For development, use http://127.0.0.1 instead of localhost
- Upon successful authentication, the Azure `user.id` field is mapped to 
the `username` field in `ab_user`
- Using personal hotmail accounts can cause issues reading JWT (see [oauthlib](https://github.com/oauthlib/oauthlib/blob/v2.1.0/oauthlib/oauth2/rfc6749/clients/web_application.py#L17))

## Azure Authentication for Operators
A json key file has been created for authentication. This enables native
Azure operators to connect to the tenant. To generate:

1. Use az cli to login
2. Run: `ad sp create-for-rbac --sdk-auth > airflow.azureauth`