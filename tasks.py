from pathlib import Path
from idcrop.clients.s3 import S3Client
from idcrop.logging import logger
from idcrop.models.constants import *

PREPROCESSED_BUCKET = "pre"
PROCESSED_BUCKET = "post"
DOWNLOAD_DIR = "images/input"
UPLOAD_DIR = "images/output"

def get_download_path(object_key):
    filename = object_key + ".jpg"
    output_path = Path(DOWNLOAD_DIR).joinpath(filename)
    return output_path

def get_upload_path(object_key):
    filename = object_key + ".jpg"
    output_path = Path(UPLOAD_DIR).joinpath(filename)
    return output_path

def download(object_key):
    file_path = get_download_path(object_key)
    try:
        logger.info(f"Downloading Object {object_key} from bucket {PROCESSED_BUCKET}...")
        client = S3Client()
        result = client.download_file(PREPROCESSED_BUCKET, object_key, file_path)
        if result is False:
            raise Exception
    except Exception as e:
        logger.error(f"Could not download file {object_key} from bucket {PREPROCESSED_BUCKET}: {e.__traceback__.tb_lineno}:{e}")
        return False
    logger.trace(f"Downloaded file {object_key} from bucket {PROCESSED_BUCKET}")
    return True

def upload(object_key):
    file_path = get_upload_path(object_key)
    try:
        logger.info(f"Uploading Object {object_key} to bucket {PROCESSED_BUCKET}...")
        client = S3Client()
        result = client.upload_file(file_path, PROCESSED_BUCKET, object_key)
        if result is False:
            raise Exception
    except Exception as e:
        logger.error(f"Could not upload file {object_key} to bucket {PREPROCESSED_BUCKET}: {e.__traceback__.tb_lineno}:{e}")
        return False
    logger.trace(f"Uploaded file {object_key} to bucket {PROCESSED_BUCKET}")
    return True

def detect(image):
    pass

def cutout():
    pass


def process(object_key):
    download(object_key)
    image_path = get_download_path(object_key)
    image = cv2.imread(image_path)