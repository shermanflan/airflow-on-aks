#!/bin/bash -eux

# Create new ACR
#az acr create \
#  --resource-group $RESOURCE_GROUP \
#  --name $REGISTRY \
#  --admin-enabled true \
#  --sku Basic \
#  -l "$LOCATION" \
#  --subscription "$SUBSCRIPTION" \
#  --verbose

# Build and publish docker image to ACR
#az acr build --registry $REGISTRY --image $IMAGE .

# Using new Compose-CLI
# See: https://docs.docker.com/engine/context/aci-integration/
# See: https://github.com/docker/compose-cli
#docker login azure
#docker context create aci cloud-aci \
#  --subscription-id $SUBSCRIPTION \
#  --resource-group $RESOURCE_GROUP \
#  --location $LOCATION

#docker compose up \
#  --context cloud-aci \
#  --file $YAML_CONFIG \
#  --project-name $CONTAINER_GROUP

#docker compose down \
#  --context cloud-aci \
#  --file $YAML_CONFIG \
#  --project-name $CONTAINER_GROUP

# Alternative publish using native Docker
#docker login $REGISTRY_URL
#docker tag python-cds $REGISTRY_URL/$IMAGE
#docker push $REGISTRY_URL/$IMAGE

# Alternative using YAML file.
#az container create \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION \
#  --file $YAML_CONFIG \
#  --verbose

# Start container instance
#az container start -n $CONTAINER_GROUP \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION \
#  --verbose --debug

# Assign security role to a principal.
#az role assignment create \
#  --role Contributor \
#  --assignee $PRINCIPAL \
#  --subscription $SUBSCRIPTION \
#  --scope $APP_SCOPE

# TODO: Clean up resources
#az container delete \
#  --name $CONTAINER_GROUP \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION