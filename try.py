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
from filters import blur
import json
from utils import NumpyDatatypesEncoder

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

    # Create a Person object and run tests
    person = Person(image)
    if not person.RESULTS.passed:
        end = time.time()
        for err in person.RESULTS.errors:
            logger.error(err['message_ar'])
        logger.error(f"Image {file_name} failed to process. Did not pass the tests. Reasons:{', '.join([str(err['message']) for err in person.RESULTS.errors])} Time taken: {end - start} seconds.")
        return None

    # Check if a face was detected
    if not person.RESULTS.face.detected:
        end = time.time()
        for err in person.RESULTS.errors:
            logger.error(err['message_ar'])
        logger.error(f"Image {file_name} failed to process. No face detected. Time taken: {end - start} seconds.")
        return None

    # Crop the image
    crop_result, cropped_image = Crop(image, person.INFO).crop()
    if not crop_result.success:
        end = time.time()
        logger.error(f"Image {file_name} failed to process. Could not crop the image. Reasons:{', '.join([str(i) for i in crop_result.errors])} Time taken: {end - start} seconds.")
        return None

    # Compress the cropped image and save it
    saved_image = compress(cropped_image, output_dir, output_filename=file_name, quality_suffix=True)
    if not saved_image.success:
        end = time.time()
        logger.error(f"Image {file_name} failed to process. Time taken: {end - start} seconds.")
        return None

    # Blur the cropped image and save it
    blurred_image = blur(cropped_image)
    cv2.imwrite(os.path.join(output_dir, file_name.split('.')[0] + "_blurred." + file_name.split('.')[-1]), blurred_image)

    # Log the results and return the log
    end = time.time()
    log = {
        "detection" : person.RESULTS.dict(),
        "crop" : crop_result.dict(),
        'save' : saved_image.dict(),
    }
    logger.success(f"Image {file_name} processed successfully. Time taken: {end - start} seconds.")
    logger.trace(log)
    return log


# for file in sorted(os.listdir("images/input"), key=lambda x: int(x.split(".")[0])):
#     process_image(os.path.join("images/input", file), "images/output")

logs = {}

logs['1'] = process_image(os.path.join("images/input", "1.jpg"), "images/output")
logs['2'] = process_image(os.path.join("images/input", "2.jpg"), "images/output")
logs['3'] = process_image(os.path.join("images/input", "3.jpg"), "images/output")
logs['4'] = process_image(os.path.join("images/input", "4.jpg"), "images/output")
logs['18'] = process_image(os.path.join("images/input", "18.jpg"), "images/output")
logs['19'] = process_image(os.path.join("images/input", "19.jpg"), "images/output")
logs['20'] = process_image(os.path.join("images/input", "20.jpg"), "images/output")
logs['21'] = process_image(os.path.join("images/input", "21.jpg"), "images/output")

json.dump(logs, open(os.path.join("result_example.json"), "w", encoding="utf-8"), cls=NumpyDatatypesEncoder)

# from clients.picwish import CutoutApiClient

# client = CutoutApiClient()
# logger.info("Uploading image...")
# task_id = client.upload_image_async(image_file=open("images/output/13.jpg", 'rb'), format="jpg")
# result = client.poll_cutout_result(task_id)
# if result.get('data').get("state") == 1:
#     client.download_result_image(result.get('data').get("image"), "images/output/13_cut.jpg")