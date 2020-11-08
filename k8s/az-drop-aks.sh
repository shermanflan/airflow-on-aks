#!/bin/bash

echo "Deleting $RESOURCE_GROUP"

az group delete \
    --name $RESOURCE_GROUP
