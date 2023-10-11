import time
import cv2, os

import numpy
from models import Person
from crop import Crop
from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


# for file in sorted(os.listdir("images/input"), key=lambda x: int(x.split(".")[0])):
for file in [
            # "0.jpg", "8.jpg","10.jpg", "12.jpg", "14.jpg", "17.jpg",
             "19.jpg",
            #  "28.jpg", "30.jpg",
             "31.jpg"]:
    image = cv2.imread(f"images/input/{file}")
    with suppress_stdout():
        person = Person(image)
        cv2.imwrite(f"images/output/{file}", image)
    if person.RESULTS.face.detected:
        start = time.time()
        print(f"Processing {file}:")
        # print(person.INFO)
        # print(person.RESULTS)
        cropped_image = Crop(image, person.INFO).crop()
        file_extension = file.split(".")[1]
        file_name = file.split(".")[0]
        if cropped_image is not None:
            cv2.imwrite(f"images/output/{file_name}-cropped.{file_extension}", cropped_image)
        print(f"{time.time() - start} seconds")
        print()





