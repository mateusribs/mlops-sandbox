import logging
import os

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def upload_model_to_s3(model_path: str, bucket_name: str, object_name: str) -> None:
    """Uploads the trained model to an S3 bucket.
    
    Args:
        model_path (str): Local path to the trained model file.
        bucket_name (str): Name of the S3 bucket to upload the model to.
        object_name (str): S3 object name for the uploaded model.
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        aws_access_key_id=os.environ["LOCALSTACK_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["LOCALSTACK_SECRET_ACCESS_KEY"],
        region_name=os.environ["LOCALSTACK_REGION_NAME"],
    )
    if bucket_name not in [bucket["Name"] for bucket in s3.list_buckets().get("Buckets", [])]:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Created bucket: {bucket_name}")

    s3.upload_file(model_path, bucket_name, object_name)
    logger.info(f"Uploaded model to s3://{bucket_name}/{object_name}")
