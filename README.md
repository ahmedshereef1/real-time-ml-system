# Real Time ML System - Crypto Price Predictor

Crypto Price Predictor is a real-time ML system that ingests market data and news, transforms it into features, and supports training and serving price prediction models. The codebase is organized as a set of microservices and deployment manifests so you can run the pipeline locally or on Kubernetes.

Data source reference: [Kraken WebSocket API (Trade)](https://docs.kraken.com/api/docs/websocket-v2/trade)

![trades](https://github.com/user-attachments/assets/bcdb5af3-eb7f-4433-8e2e-22d42422c48b)

![candles](https://github.com/user-attachments/assets/3e4b6fd5-8a11-453c-9a77-a58aa0a8a59e)

![ti](https://github.com/user-attachments/assets/2628638e-a507-4458-8cdf-ba19cd6d2ac5)

## What this project does
- Streams crypto trades and news in real time.
- Aggregates trades into candles and computes technical indicators.
- Extracts sentiment signals from news.
- Trains models (predictor service) and serves predictions (prediction API).
- Provides deployment scripts and manifests for dev and prod clusters.

## Architecture overview
Two main pipelines feed features into model training and inference:

1. Market data: trades -> candles -> technical indicators -> model features
2. News data: news -> sentiment analysis -> sentiment signals -> model features

The services communicate through a message bus and can be deployed independently.

## Services
- trades (Python): Ingests real-time trade data and publishes trade events.
- candles (Python): Aggregates trades into OHLCV candles.
- technical_indicators (Python): Calculates indicators from candles.
- news (Python): Ingests crypto news articles.
- news-sentiment (Python): Scores news for sentiment and emits signals.
- predictor (Python): Trains models; integrates with MLflow.
- prediction-api (Rust): Serves predictions via an API.
- prediction-generator: Generates predictions (batch or streaming, deployment-driven).
- training-pipeline: Orchestrates training runs.

## Repository layout
- services/: Python and Rust microservices.
- docker/: Dockerfiles for each service.
- deployments/: Kubernetes manifests for dev and prod.
- scripts/: Build and deploy helpers.
- dashboards/: Grafana dashboards.

## Local development
Prerequisites:
- Python 3.12+
- uv (recommended)
- Docker
- Make

Run a service locally (not Dockerized):
```bash
make dev service=<service_name>
```

Linting:
```bash
make lint
```

## Configuration
- Service-specific configuration lives in each service folder (for example settings.env).
- The predictor service uses an .env.local file for MLflow credentials; copy and fill it in:
```bash
cp services/predictor/.env.local.sample services/predictor/.env.local
```

## Build and deploy
Build and push a Docker image:
```bash
make build-and-push image_name=<image> env=<dev|prod>
```

Deploy a service:
```bash
make deploy service=<service> env=<dev|prod>
```

Kubernetes manifests are under `deployments/` for both dev and prod environments.

## Status
The streaming pipelines and deployments are in place. Model training and inference are available through the predictor and prediction-api services, with ongoing iteration across data sources, features, and deployments.

