# Runs the trades service as a standalone Pyton app (not Dockerized)
dev: 
	uv run services/$(service)/src/$(service)/main.py

push:
	kind load docker-image ${service}:dev --name rwml-34fa

build:
	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

deploy: build push
	kubectl apply -f deployments/dev/${service}/${service}-d.yaml
	kubectl rollout restart deployment/${service}

lint:
	ruff check . --fix
