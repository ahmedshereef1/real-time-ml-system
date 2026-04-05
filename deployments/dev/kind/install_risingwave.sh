#!/bin/bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-risingwave}"
RELEASE_NAME="${RELEASE_NAME:-risingwave}"
CHART="${CHART:-risingwavelabs/risingwave}"
VALUES_FILE="${VALUES_FILE:-manifests/risingwave-values.yaml}"
HELM_TIMEOUT="${HELM_TIMEOUT:-10m}"
WAIT_FOR_READY="${WAIT_FOR_READY:-true}"

helm repo add risingwavelabs https://risingwavelabs.github.io/helm-charts/ --force-update

helm repo update

wait_arg="--wait"
if [[ "$WAIT_FOR_READY" != "true" ]]; then
	wait_arg="--wait=false"
fi

helm upgrade --install \
	--create-namespace \
	"$wait_arg" \
	--timeout "$HELM_TIMEOUT" \
	--debug \
	"$RELEASE_NAME" "$CHART" \
	--namespace "$NAMESPACE" \
	-f "$VALUES_FILE"