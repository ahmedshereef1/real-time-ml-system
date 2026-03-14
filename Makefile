# Runs the trades service as a standalone Python app (not Dockerized)
dev: 
	uv run services/$(service)/src/$(service)/main.py

push:
	kind load docker-image ${service}:dev --name rwml-34fa

build:
	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

deploy: build push
	kubectl apply -f deployments/dev/${service}/${service}-d.yaml
	kubectl rollout restart deployment/${service}
	@echo "Cleaning up old import images from kind cluster..."
	-docker exec rwml-34fa-control-plane sh -c "crictl images | grep 'import-' | awk '{print \$$3}' | xargs -r crictl rmi" 2>/dev/null || true
	@echo "Cleaning up dangling Docker images..."
	-docker image prune -f
	@echo "Cleaning up build cache..."
	-docker builder prune -f --filter "until=24h"
	@echo "Cleanup complete!"

lint:
	ruff check . --fix

# Manual cleanup command for when container gets too large
clean:
	@echo "Running full Docker cleanup..."
	docker system prune -af
	@echo "Cleaning ALL import images from kind cluster..."
	-docker exec rwml-34fa-control-plane sh -c "crictl images | grep 'import-' | awk '{print \$$3}' | xargs -r crictl rmi" 2>/dev/null || true
	@echo "Full cleanup complete!"

# Check disk usage
check-size:
	@echo "Docker disk usage:"
	@docker system df
	@echo ""
	@echo "Kind cluster images:"
	@docker exec rwml-34fa-control-plane crictl images
	@echo ""
	@echo "Docker build cache:"
	@docker builder du