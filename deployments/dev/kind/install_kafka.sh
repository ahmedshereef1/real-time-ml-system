#!/bin/bash

kubectl get namespace kafka || kubectl create namespace kafka

kubectl apply -f https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.43.0/strimzi-cluster-operator-0.43.0.yaml -n kafka

# Wait for Strimzi CRDs to be ready
echo "Waiting for Strimzi CRDs to be ready..."
kubectl wait --for=condition=established crd/kafkas.kafka.strimzi.io --timeout=120s
kubectl wait --for=condition=established crd/kafkanodepools.kafka.strimzi.io --timeout=120s

# Wait for Strimzi operator to be ready
echo "Waiting for Strimzi operator to be ready..."
kubectl rollout status deployment/strimzi-cluster-operator -n kafka --timeout=300s
echo "Giving Strimzi operator time to initialize..."
sleep 15

# This dev cluster runs a single Strimzi operator replica, so leader election
# only adds lease flapping and crash loops when the lease cannot be renewed.
kubectl -n kafka set env deployment/strimzi-cluster-operator STRIMZI_LEADER_ELECTION_ENABLED=false
kubectl rollout status deployment/strimzi-cluster-operator -n kafka --timeout=300s

kubectl apply -f manifests/kafka-e11b.yaml

# Wait for Kafka broker to be ready
echo "Waiting for Kafka broker to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=kafka-e11b -n kafka --timeout=300s
echo "Kafka is ready!"