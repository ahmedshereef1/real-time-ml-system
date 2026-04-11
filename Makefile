############################################################################
## Development
############################################################################
# Runs the trades service as a standalone Python app (not Dockerized)
dev: 
	uv run services/$(service)/src/$(service)/main.py

# Builds and pushes the docker image to the given environment
build-and-push:
	./scripts/build-and-push-image.sh ${image_name} ${env}

# Deploys a service to the given environment
deploy:
	./scripts/deploy.sh ${service} ${env}

lint:
	ruff check . --fix

# build-for-dev:
# 	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

# run: build-for-dev
# 	docker run -it ${service}:dev

# push-for-dev:
# 	kind load docker-image ${service}:dev --name rwml-34fa

# deploy-for-dev: build-for-dev push-for-dev
# 	kubectl delete -f deployments/dev/${service}/${service}-d.yaml --ignore-not-found=true
# 	kubectl apply -f deployments/dev/${service}/${service}-d.yaml

############################################################################
## Production
############################################################################
# build-and-push-for-prod:
# 	export BUILD_DATE=$$(date +%s); \
# 	docker buildx build --push --platform linux/amd64 \
# 	-t ghcr.io/ahmedshereef1/${service}:0.1.3-beta.$$BUILD_DATE \
# 	-f docker/${service}.Dockerfile .

# deploy-for-prod:
# 	kubectl delete -f deployments/prod/${service}/${service}.yaml --ignore-not-found=true
# 	kubectl apply -f deployments/prod/${service}/${service}.yaml

