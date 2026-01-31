format:
	@uv run ruff format src tests

lint:
	@uv run ruff check src tests --fix

train-models:
	@uv run src/train/anomaly_classifier_pipeline.py
	@uv run src/train/level_classifier_pipeline.py

load_test:
	@bash tests/load_tests/run_test.sh

up:
	@docker compose down
	@sudo rm -rf grafana-data/
	@docker compose up -d --build
	@sleep 10
	@bash cleanup.sh
	@bash deploy.sh