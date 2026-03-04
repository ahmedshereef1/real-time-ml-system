#!/bin/bash

kubectl get namespace kafka || kubectl create namespace kafka

kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

kubectl apply -f manifests/kafka-e11b.yaml