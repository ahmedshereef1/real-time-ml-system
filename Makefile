# Runs the trades service as a standalone Pyton app (not Dockerized)
dev: 
	uv run services/trades/src/trades/main.py

build:
	docker build -t trades:dev -f docker/trades.Dockerfile .