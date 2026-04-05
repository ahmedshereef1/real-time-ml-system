#!/bin/bash

kubectl apply -f manifests/kafka-ui-all-in-one.yaml

# Wait for Kafka UI to be ready
echo "Waiting for Kafka UI to be ready..."
kubectl wait --for=condition=ready pod -l app=kafka-ui -n kafka --timeout=300s

echo "Kafka UI is ready!"
