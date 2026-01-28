format:
	@uv run ruff format src tests

lint:
	@uv run ruff check src tests --fix

train-models:
	@uv run src/train/anomaly_classifier_pipeline.py
	@uv run src/train/level_classifier_pipeline.py

load_test:
	@uv run locust -f tests/load_tests/locustfile.py
