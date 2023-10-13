import time
import cv2, os
from models import Person
from crop import Crop
from contextlib import contextmanager
import sys, os
from log_config import logger
from save import compress
from exceptions import SaveError
from pathlib import Path


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

from log_config import logger

def process_image(file_path, output_dir):
    start = time.time()
    file_name = Path(file_path).name
    image = cv2.imread(file_path)
    logger.info(f"Processing image: {file_name}...")
    person = Person(image)
    cropped_image = None
    saved_image = None
    if person.RESULTS.face.detected:
        cropped_image = Crop(image, person.INFO).crop()
        if cropped_image.success:
            saved_image = compress(cropped_image.image, output_dir, output_filename=file_name, quality_suffix=True)
            end = time.time()
            if not saved_image.success:
                logger.error(f"Image {file_name} failed to process. . Time taken: {end - start} seconds.")
            else:
                logger.success(f"Image {file_name} processed successfully. Time taken: {end - start} seconds.")
        else:
            end = time.time()
            logger.error(f"Image {file_name} failed to process. Could not crop the image. Reasons:{', '.join([str(i) for i in cropped_image.errors])} Time taken: {end - start} seconds.")
    else:
        end = time.time()
        logger.error(f"Image {file_name} failed to process. No face detected. Time taken: {end - start} seconds.")

    log = {
        'file' : file_name,
        "detection" : person.INFO.dict(),
        "tests" : person.RESULTS.dict(),
        "crop" : cropped_image.dict() if cropped_image is not None else None,
        'save' : saved_image.dict() if saved_image is not None else None,
    }
    logger.trace(log)
    return log

