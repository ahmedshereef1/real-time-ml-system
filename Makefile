# Runs the trades service as a standalone Python app (not Dockerized)
dev:
	uv run services/trades/src/trades/main.py

# Build Docker image
build:
	docker build -t trades:dev -f docker/trades.Dockerfile .

# Load image into kind cluster
push:
	kind load docker-image trades:dev --name rwml-34fa

# Deploy to Kubernetes without rebuilding
deploy:
	kubectl apply -f deployments/dev/trades/trades-d.yaml
	kubectl rollout restart deployment/trades

# Full pipeline when needed
release: build push deploy

lint:
	ruff check . --fix
