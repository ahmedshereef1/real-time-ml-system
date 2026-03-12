# Runs the trades service as a standalone Python app (not Dockerized)
dev:
	uv run services/$(service)/src/$(service)/main.py

# Build Docker image
build:
	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

# Load image into kind cluster
push:
	kind load docker-image ${service}:dev --name rwml-34fa

# Deploy to Kubernetes without rebuilding
deploy: push
	kubectl apply -f deployments/dev/${service}/${service}-d.yaml
	kubectl rollout restart deployment/${service}

# Full pipeline when needed
release: build push deploy

lint:
	ruff check . --fix
