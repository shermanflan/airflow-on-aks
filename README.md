# Airflow on Azure Kubernetes Service
The primary goal of this repo is to provide the necessary scripts and 
manifests required to automate a deployment of Airflow on AKS. Key to
this enterprise deployment is supporting TLS termination via nginx ingress 
and OAuth2 via Azure Active Directory.

In addition, the following additional features are included. 

- Local development via docker-compose
- Support for Azure Container Instances

## Project Goals
Key objectives include:

- Deploy Airflow configured to use the Celery Executor
- Deploy Airflow configured to use the Kubernetes Executor
- Use the nginx [ingress](https://docs.microsoft.com/en-us/azure/aks/ingress-tls) 
with tls termination provided by the managed helm chart
- Enable certificate management using the [cert-mgr](https://cert-manager.io/docs/installation/kubernetes/) 
controller provided by the managed helm chart
- Use a DNS zone with a registered domain (rikguz.com)
- Secure Airflow using OAuth2 via Azure Active Directory
- Include a plugin with operators, hooks, etc. to support orchestration
in Azure

## Pre-requisites
In order to use the manifest files in this repo, a few pre-requisites
are required.

1. An Azure account with access to the az cli
2. If using tls-termination and OAuth2, then a DNS zone is necessary
preferably with a registered domain
3. A storage account for hosting Airflow volumes as Azure file systems
4. An Application Registration in Azure Active Directory for OAuth2

## Airflow on AKS using Celery
A working version of Airflow 1.10.13 has been configured to run under the
Azure Kubernetes Service in `CeleryExecutor` mode.

1. The manifests under [k8s](k8s) together define an Airflow configuration 
using the Celery Executor
2. Volume claims are defined in [k8s/base](k8s/base). 4 [volumes](k8s/base/aks-volumes.yaml) 
are configured against an Azure File Share as follows.
    - Store dags under volume `azure-file-dags`
    - Store initialization scripts under volume `azure-file-scripts`
    - Store a database initialization indicator under volume `az-file-init`
    - Store logs under volume `azure-file-logs`
3. An nginx ingress is defined under [k8s/ingress-nginx](k8s/ingress-nginx/aks-airflow-ingress-tls.yaml),
configured with tls termination. 
4. Automated certificate generation is configured against the 
[Let's Encrypt](https://cert-manager.io/docs/tutorials/acme/ingress/)
issuer using the manifests under [k8s/cert-manager](k8s/cert-manager)
5. The Airflow image used by the manifests is a pre-baked version 
configured with RBAC and OAuth2 using a modified 
[webserver_config.py](bootstrap/webserver_config.py) 
file. See the [Dockerfile](./Dockerfile).
6. The K8s cluster is configured with RBAC. As such, a highly privileged
service account and cluster role [binding](k8s/airflow/aks-airflow-rbac.yaml) 
have been defined for the Airflow web server, scheduler, and workers. For
production, using more fine-grained access controls may be more suitable.
7. In order to simplify configuration management, the manifests for the 
airflow webserver, scheduler, and workers refer to a [configuration map](k8s/airflow/celery/aks-airflow-configmap.yaml)
8. As this is a test configuration, both [postgreSQL](k8s/airflow/aks-postgres.yaml) 
and [redis](k8s/airflow/aks-redis.yaml) 
deployments have been defined as cluster services. For production, these 
would probably be deployed as services outside the cluster using PaaS.

### Deployment
Assuming all of the pre-requisites are satisfied, the Airflow deployment can
be initiated by following these steps. The key script is [`az-add-aks.sh`](k8s/az-add-aks.sh),
and it relies on a number of environment variables, which need to be 
configured according to your Azure environment.

1. Upload the scripts under [bootstrap](bootstrap) to an Azure file share
referenced by the volumes defined in [k8s/base](k8s/base)
2. Upload any dags to an Azure file share referenced by the volumes 
defined in [k8s/base](k8s/base)
3. Run the [`az-add-aks.sh`](k8s/az-add-aks.sh) script to build an AKS 
cluster along with a container registry, helm chart installations, and 
DNS zone updates
4. Then, run the [`aks-install-airflow-celery.sh`](k8s/aks-install-airflow-celery.sh) 
script to deploy Airflow, the nginx ingress, and the cert-mgr certificate 
controller
5. Your deployment should be up and running
6. To delete the cluster, run the [`aks-drop.sh`](k8s/az-drop-aks.sh)
script

## [RBAC](https://github.com/rolanddb/airflow-on-kubernetes/blob/master/README.md#rbac)
"If your cluster has [RBAC](https://kubernetes.io/docs/admin/authorization/rbac/) 
turned on, and you want to launch Pods from Airflow, you will need to bind 
the appropriate roles to the serviceAccount of the Pod that wants to schedule 
other Pods. Typically, this means that the Workers (when using CeleryExecutor) 
or the Scheduler (using LocalExecutor or the new KubernetesPodExecutor) need 
extra permissions. You'll need to grant the 'watch/create' verbs on Pods."

See [here](https://medium.com/@ipeluffo/running-apache-airflow-locally-on-kubernetes-minikube-31f308e3247a#:~:text=AIRFLOW__KUBERNETES__WORKER_CONTAINER_REPOSITORY%20%3A%20all%20env%20vars%20with%20the,be%20run%20on%20a%20Pod.) 
for an example permissions declaration.

## Azure Authentication for Web UI
The airflow configuration uses the OAuth2 authorization code flow facilitated 
by Flask-AppBuilder. A custom [web config](bootstrap/webserver_config.py) has 
been setup to use the OAuth2 AUTH_TYPE. In order for the OAuth2 flow to work, 
an application registration is required with the following properties (all 
other properties can be left as per defaults).

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
- Using personal hotmail accounts can cause issues reading the JWT (see 
[oauthlib](https://github.com/oauthlib/oauthlib/blob/v2.1.0/oauthlib/oauth2/rfc6749/clients/web_application.py#L17))

## Azure Plugin
A custom set of operators and hooks have been added under the [plugins](plugins)
folder. Key features include:

- Azure Data Factory [operator](plugins/bsh_azure/operators/azure_data_factory_operator.py)
- Azure Data Factory [hook](plugins/bsh_azure/hooks/azure_data_factory_hook.py)
- Azure Data Factory [sensor](plugins/bsh_azure/sensors/azure_data_factory_sensor.py)
- Box.com [hook](plugins/bsh_azure/hooks/box_hook.py)
- Box.com [sensor](plugins/bsh_azure/sensors/box_sensor.py)

### Azure Authentication for Operators
A json key file has been created for authentication. This enables 
`contrib` Azure operators to connect to the tenant. To generate:

1. Use az cli to login
2. Run: `az ad sp create-for-rbac --sdk-auth > airflow.azureauth`

### Box.com Authentication for BoxHook
A json key file has been created for authentication and loaded as secret
[box_secret](https://github.com/shermanflan/airflow-on-aks/blob/master/k8s/az-add-aks.sh#L153)
in AKS. This enables the custom [`BoxHook`](plugins/bsh_azure/hooks/box_hook.py) 
to authenticate to the Box.com tenant. To re-generate the key file, follow 
these steps:

1. Log into the box.com [developer console](https://rescare.app.box.com/developers/console)
using a personal login
2. Create an OAuth2 application
3. Go to Configuration
4. Under `Add and Manage Public Keys`, remove the current key and click
`Genereate a Public/Private Keypair`.
5. This will download a new json config file
6. This file should be saved locally and used as the basis for an AKS 
secret

## Deploy to Azure Container Instances
It is possible to deploy a set of Airflow containers to a single ACI group. 
However, the CPU/Memory 
[limits](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-region-availability)
imposed on the group make this impractical for all but the simplest use cases.
In any event, this may be a plausible solution for local dev/test scenarios.

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

Sample scripts for setting this up can be found in the [aci](aci/) folder. 
For more details, refer to the 
[ACI documentation](https://docs.microsoft.com/en-us/azure/container-instances/tutorial-docker-compose).

## Docker Compose
Multiple `docker-compose.yaml` configurations have been created for local
dev/test purposes.

- Local single-tier development (default): LocalExecutor, single host
    - [`docker-compose.yaml`](docker-compose.yml)
- Local multi-tier template: CeleryExecutor, postgres/redis backends
    - [`docker-compose-multi-tier.yaml`](docker-compose-multi-tier.yml)
- Azure Container Instances: CeleryExecutor, postgres/redis backends, 
ACI-compatible
    - [`docker-compose-aci.yaml`](aci/docker-compose-aci.yml)

## Future Enhancements

- Use [git repo sync](https://docs.bitnami.com/azure-templates/infrastructure/apache-airflow/configuration/sync-dags/)
for dags
- Use the [Kubernetes Executor](https://airflow.readthedocs.io/en/1.10.12/executor/kubernetes.html) 
in an AKS deployment
- Implement an MS Teams operator
- Create an airflow2 version upon release
- Deploy using the "official" Airflow helm chart

