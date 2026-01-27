import boto3
import pendulum
from loguru import logger
import os


def register_model_version(
    model_name: str,
    version: str,
    s3_bucket: str,
    s3_key: str,
    model_type: str,
    table_name: str = "model-registry",
):
    """
    Register a model version in DynamoDB with simple versioning.

    Args:
        model_name: Name of the model
        version: Simple version
        s3_bucket: S3 bucket containing model artifact
        s3_key: S3 key (path) to model JSON file
        model_type: Type of model class
        table_name: DynamoDB table name

    DynamoDB Schema:
    - PK (HASH): model_name
    - SK (RANGE): version
    - Attributes: s3_bucket, s3_key, trained_at, model_type
    """
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        aws_access_key_id=os.environ["LOCALSTACK_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["LOCALSTACK_SECRET_ACCESS_KEY"],
        region_name=os.environ["LOCALSTACK_REGION_NAME"],
    )
    table = dynamodb.Table(table_name)

    item = {
        "model_name": model_name,
        "version": version,
        "s3_bucket": s3_bucket,
        "s3_key": s3_key,
        "trained_at": pendulum.now("UTC").to_iso8601_string(),
        "model_type": model_type,
    }

    table.put_item(Item=item)

    logger.info(f"Registered {model_name} version {version}")
    return version
