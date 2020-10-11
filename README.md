# airflow-local
Repo for running a local version of airflow for development purposes.

## To Do

- Use git repo sync for dags. 
See [here](https://docs.bitnami.com/azure-templates/infrastructure/apache-airflow/configuration/sync-dags/)
- Use k8s executor in an AKS deployment.
    - https://airflow.readthedocs.io/en/1.10.12/executor/kubernetes.html
- (Unrelated) Use 
[AzureContainerInstanceHook](https://github.com/apache/airflow/blob/v1-10-stable/airflow/contrib/hooks/azure_container_instance_hook.py)
as a reference for implementing an Azure Functions scheduler.
- Implement a Teams operator.
- Use [`DebugExecutor`](https://airflow.readthedocs.io/en/1.10.12/executor/debug.html) to debug DAG in IDE.
- Consider [plugins](https://airflow.readthedocs.io/en/1.10.12/plugins.html)
as the approach for extending airflow.
- May need to enable [SSL](https://airflow.readthedocs.io/en/1.10.12/security.html#ssl).
- Add a [reverse proxy](https://www.cloudflare.com/learning/cdn/glossary/reverse-proxy/)
    - [nginx](https://www.nginx.com/)
    - Azure options
- Create an airflow2 version

## Docker Compose
Multiple `docker-compose.yaml` configurations have been created for different
use-cases.

- Local development (default): LocalExecutor, single host
    - `docker-compose.yaml`
- Production template: CeleryExecutor, postgres/redis backends
    - `docker-compose-multi-node.yaml`
- Azure Container Instances: CeleryExecutor, postgres/redis backends, 
ACI-compatible
    - `docker-compose-aci.yaml`
- Azure Kubernetes Service: KubernetesExecutor, postgres/redis backends, 
AKS-compatible
    - `docker-compose-aks.yaml`
    
## Azure Authentication for Web UI
This uses the OAuth2 authorization code flow facilitated by Flask-AppBuilder. 
In order for the OAuth2 flow to work, an application registration is required 
with the following properties (all other properties can be left as per 
defaults).

- API permissions:
    - Graph API: 
        - User.Read (Delegated)
- Redirect URI (port is ignored):
    - http://[your airflow URI]/oauth-authorized/azure

Per Microsoft [guidelines](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow), 
the following should be kept in mind.

- Redirect URI may need to be https for non-localhost URIs
- For development, use http://127.0.0.1 instead of localhost
- Upon successful authentication, the Azure `user.id` field is mapped to 
the `username` field in `ab_user`
- Using personal hotmail accounts can cause issues reading JWT (see [oauthlib](https://github.com/oauthlib/oauthlib/blob/v2.1.0/oauthlib/oauth2/rfc6749/clients/web_application.py#L17))

## Azure Authentication for Operators
A json key file has been created for authentication. This enables `contrib`
Azure operators to connect to the tenant. To generate:

1. Use az cli to login
2. Run: `ad sp create-for-rbac --sdk-auth > airflow.azureauth`

## Deploy to Azure Container Instances
It is possible to deploy a set of Airflow containers to a single ACI group. 
However, the CPU/Memory 
[limits](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-region-availability)
imposed on the group make this impractical for all but the simplest use cases.
In any event, this may be a plausible solution for basic dev/test scenarios.

- Install the [Docker Compose CLI](https://github.com/docker/compose-cli)
    - This is in beta; see [here](https://docs.docker.com/engine/context/aci-integration/)
    for additional info.
- Log in to Azure: `docker login azure`
- Create a context: 
```
docker context create aci cloud-aci \
  --subscription-id $SUBSCRIPTION \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```
- Deploy to ACI: the file argument should point to a standard `docker-compose.yaml`
```
docker compose up \
  --context cloud-aci \
  --file $YAML_CONFIG \
  --project-name $CONTAINER_GROUP
```
- Dispose ACI resources:
```
docker compose down \
  --context cloud-aci \
  --file $YAML_CONFIG \
  --project-name $CONTAINER_GROUP
```

For more details, refer to the [ACI documentation](https://docs.microsoft.com/en-us/azure/container-instances/tutorial-docker-compose).

## Deploy to Azure Kubernetes Service
TBD
