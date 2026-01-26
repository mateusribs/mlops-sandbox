format:
	@uv run ruff format src

lint:
	@uv run ruff check src --fix

train-models:
	@uv run src/train/anomaly_classifier_pipeline.py
	@uv run src/train/level_classifier_pipeline.py

