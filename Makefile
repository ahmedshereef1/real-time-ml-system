############################################################################
## Development
############################################################################
# Runs the trades service as a standalone Python app (not Dockerized)
dev: 
	uv run services/$(service)/src/$(service)/main.py

build-for-dev:
	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

run: build-for-dev
	docker run -it ${service}:dev

push-for-dev:
	kind load docker-image ${service}:dev --name rwml-34fa

deploy-for-dev: build-for-dev push-for-dev
	kubectl delete -f deployments/dev/${service}/${service}-d.yaml --ignore-not-found=true
	kubectl apply -f deployments/dev/${service}/${service}-d.yaml

############################################################################
## Production
############################################################################
build-and-push-for-prod:
	export BUILD_DATE=$$(date +%s); \
	docker buildx build --push --platform linux/amd64 \
	-t ghcr.io/ahmedshereef1/${service}:0.1.3-beta.$$BUILD_DATE \
	-f docker/${service}.Dockerfile .

deploy-for-prod:
	kubectl delete -f deployments/prod/${service}/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployments/prod/${service}/${service}.yaml

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