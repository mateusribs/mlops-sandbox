# API Gateway Configuration
API_GATEWAY_CONFIG = {
    "endpoints": {
        "classify_anomaly": "/anomaly",
        "classify_level": "/level",
    },
}

# Lambda Function Configurations (used for payload generation)
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
