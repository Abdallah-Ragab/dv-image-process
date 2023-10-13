from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from log_config import logger

load_dotenv()

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

s3 = boto3.resource(
    service_name='s3',
    aws_access_key_id='<PUT_YOUR_KEY>',
    aws_secret_access_key='<PUT_YOUR_SECRET>',
    endpoint_url='https://s3.tebi.io'
)

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = Path(file_name).name

    logger.info(f"Uploading file {file_name} to bucket {bucket}...")
    bucket = s3.Bucket(bucket)
    # Upload the file
    try:
        response = bucket.upload_file(file_name, object_name)
    except ClientError as e:
        logger.error(f"Could not upload file {file_name} to bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
        return False
    return True

def download_file(bucket, object_name, file_name):
    """Download a file from an S3 bucket

    :param bucket: Bucket to download from
    :param object_name: S3 object name
    :param file_name: Local file name to save to
    :return: True if file was downloaded, else False

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
    """
    logger.info(f"Downloading file {object_name} from bucket {bucket}...")
    bucket = s3.Bucket(bucket)
    # Download the file
    try:
        bucket.download_file(object_name, file_name)
    except ClientError as e:
        logger.error(f"Could not download file {object_name} from bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
        return False
    return True

def create_preassigned_upload_link(bucket, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket: Bucket to share
    :param object_name: S3 object name
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    """
    logger.info(f"Creating preassigned upload link for file {object_name} in bucket {bucket}...")
    # Generate a presigned URL for the S3 object
    try:
        response = s3.meta.client.generate_presigned_url('put_object',
                                                        Params={'Bucket': bucket,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
    except ClientError as e:
        logger.error(f"Could not create preassigned upload link for file {object_name} in bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
        return None

    # The response contains the presigned URL
    return response