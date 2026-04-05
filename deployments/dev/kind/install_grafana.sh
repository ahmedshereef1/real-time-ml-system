#!/bin/bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-monitoring}"
RELEASE_NAME="${RELEASE_NAME:-grafana}"
CHART="${CHART:-grafana/grafana}"
VALUES_FILE="${VALUES_FILE:-manifests/grafana-values.yaml}"
HELM_TIMEOUT="${HELM_TIMEOUT:-10m}"
WAIT_FOR_READY="${WAIT_FOR_READY:-true}"

helm repo add grafana https://grafana.github.io/helm-charts

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
	--values "$VALUES_FILE"
