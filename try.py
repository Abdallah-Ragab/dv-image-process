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
for file in sorted(os.listdir("images/input"), key=lambda x: int(x.split(".")[0])):
    start = time.time()
    image = cv2.imread(f"images/input/{file}")
    logger.info(f"Processing image: {file}...")
    person = Person(image)
    if person.RESULTS.face.detected:
        crop_obj = Crop(image, person.INFO)
        cropped_image = crop_obj.crop()
        if cropped_image is not None:
            try:
                output_dir = Path.joinpath(Path.cwd(), "images/output")
                output_filename = file
                saved = compress(cropped_image, "images/output", output_filename=output_filename)
                if not saved:
                    raise SaveError()
                end = time.time()
                logger.success(f"Image {file} processed successfully. Time taken: {end - start} seconds.")
            except SaveError as e:
                logger.error(f"Image {file} failed to process. {e.__traceback__.tb_lineno}:{e}")
        else:
            end = time.time()
            logger.error(f"Image {file} failed to process. Could not crop the image. Reasons:{', '.join([str(i) for i in crop_obj.CROP_ERRORS])} Time taken: {end - start} seconds.")
    else:
        end = time.time()
        logger.error(f"Image {file} failed to process. No face detected. Time taken: {end - start} seconds.")
    log = {
        'file' : file,
        "results" : person.RESULTS.dict(),
        "info" : person.INFO.dict(),
        'saved' : saved is not None if cropped_image is not None else None,
        'path' : saved.path if cropped_image is not None else None,
        'crop_errors' : crop_obj.CROP_ERRORS,
        'cropped' : cropped_image is not None,
        'time_taken' : end - start,
        'image_size' : saved.size if cropped_image is not None else None,
        'image_quality' : saved.quality if cropped_image is not None else None,
        'image_height' : saved.dimensions.height if cropped_image is not None else None,
        'image_width' : saved.dimensions.width if cropped_image is not None else None,
    }
    logger.trace(log)