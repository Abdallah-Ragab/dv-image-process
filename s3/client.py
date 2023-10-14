from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from log_config import logger

load_dotenv()

PUBLIC_KEY = os.getenv('S3_PUBLIC_KEY')
SECRET_KEY = os.getenv('S3_SECRET_KEY')

class S3Client:
    def __init__(self, endpoint_url):
        try:
            self.s3 = boto3.resource(
                service_name='s3',
                aws_access_key_id=PUBLIC_KEY,
                aws_secret_access_key=SECRET_KEY,
                endpoint_url=endpoint_url
            )
            self.s3.meta.client.head_bucket(Bucket=self.s3.Bucket.name)
        except ClientError as e:
            logger.error(f"Could not connect to S3 endpoint {endpoint_url}: {e.__traceback__.tb_lineno}:{e}")
            raise

    def upload_file(self, file_name, bucket, object_name=None):
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
        bucket = self.s3.Bucket(bucket)
        # Upload the file
        try:
            response = bucket.upload_file(file_name, object_name)
        except ClientError as e:
            logger.error(f"Could not upload file {file_name} to bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
            return False
        return True

    def download_file(self, bucket, object_name, file_name):
        """Download a file from an S3 bucket

        :param bucket: Bucket to download from
        :param object_name: S3 object name
        :param file_name: Local file name to save to
        :return: True if file was downloaded, else False

        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
        """
        logger.info(f"Downloading file {object_name} from bucket {bucket}...")
        bucket = self.s3.Bucket(bucket)
        # Download the file
        try:
            bucket.download_file(object_name, file_name)
        except ClientError as e:
            logger.error(f"Could not download file {object_name} from bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
            return False
        return True

    def create_preassigned_upload_link(self, bucket, object_name, expiration=3600):
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
            response = self.s3.meta.client.generate_presigned_url('put_object',
                                                            Params={'Bucket': bucket,
                                                                    'Key': object_name},
                                                            ExpiresIn=expiration)
        except ClientError as e:
            logger.error(f"Could not create preassigned upload link for file {object_name} in bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
            return None

        # The response contains the presigned URL
        return response

    def create_preassigned_get_link(self, bucket, object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object

        :param bucket: Bucket to share
        :param object_name: S3 object name
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.

        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
        """
        logger.info(f"Creating preassigned get link for file {object_name} in bucket {bucket}...")
        # Generate a presigned URL for the S3 object
        try:
            response = self.s3.meta.client.generate_presigned_url('get_object',
                                                            Params={'Bucket': bucket,
                                                                    'Key': object_name},
                                                            ExpiresIn=expiration)
        except ClientError as e:
            logger.error(f"Could not create preassigned get link for file {object_name} in bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
            return None

        # The response contains the presigned URL
        return response

    def list_objects(self, bucket):
        """List all objects in an S3 bucket

        :param bucket: Bucket to list objects from
        :return: List of object keys. If error, returns None.

        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-list-objects.html
        """
        logger.info(f"Listing objects in bucket {bucket}...")
        # List objects in the bucket
        try:
            response = self.s3.meta.client.list_objects(Bucket=bucket)
        except ClientError as e:
            logger.error(f"Could not list objects in bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
            return None

        # Extract the object keys from the response
        object_keys = []
        if 'Contents' in response:
            for obj in response['Contents']:
                object_keys.append(obj['Key'])
        return object_keys

    def delete_object(self, bucket, object_name):
        """Delete an object from an S3 bucket

        :param bucket: Bucket to delete from
        :param object_name: S3 object name
        :return: True if object was deleted, else False

        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-delete-objects.html
        """
        logger.info(f"Deleting object {object_name} from bucket {bucket}...")
        # Delete the object
        try:
            response = self.s3.meta.client.delete_object(Bucket=bucket, Key=object_name)
        except ClientError as e:
            logger.error(f"Could not delete object {object_name} from bucket {bucket}: {e.__traceback__.tb_lineno}:{e}")
            return False
        return True
