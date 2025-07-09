setup:
	@uv sync --locked

format:
	@uv run black src/
	@uv run isort src/

run:
	@uv run src/main.py

train:
	@uv run src/train.py

run_mlflow_server:
	@uv run mlflow server --host 127.0.0.1 --port 8080