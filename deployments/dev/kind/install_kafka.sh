#!/bin/bash

kubectl get namespace kafka || kubectl create namespace kafka

kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

kubectl apply -f manifests/kafka-e11b.yaml

# Wait for Kafka broker to be ready
echo "Waiting for Kafka broker to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=kafka-e11b -n kafka --timeout=300s

echo "Kafka is ready!"