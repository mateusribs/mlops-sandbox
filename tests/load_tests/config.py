LAMBDA_FUNCTIONS = {
    "classify_anomaly": {
        "name": "classify_anomaly",
        "model_name": "anomaly_classifier",
        "model_version": "v1",
    },
    "classify_level": {
        "name": "classify_level",
        "model_name": "level_classifier",
        "model_version": "v1",
    },
}

# Load test parameters
LOAD_TEST_CONFIG = {
    "users": 100,  # Number of concurrent users
    "spawn_rate": 1,  # Users spawned per second
    "run_time": "5m",  # Duration of the test
    "value_range": (0, 1000),  # Range for random values
}
