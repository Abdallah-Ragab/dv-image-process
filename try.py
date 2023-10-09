import cv2, os

import numpy
from models import Person
from contextlib import contextmanager
import sys, os

def crop_around_center_x(image, center_x, crop_size):
    crop_start = center_x - crop_size/2
    crop_end = center_x + crop_size/2
    cv2.line(image, (int(crop_start), 0), (int(crop_start), image.shape[0]), (0, 255, 0), 2)
    cv2.line(image, (int(crop_end), 0), (int(crop_end), image.shape[0]), (0, 255, 0), 2)
    return image[:, int(crop_start):int(crop_end)]
def center_face_crop_x(image, face_center=0):
    right_side = image.shape[1] - face_center
    left_side = face_center
    crop_size_side = min(right_side, left_side)
    return crop_around_center_x(image, face_center, crop_size_side*2)


def crop(file, image, info):
    head_top = info.head.top
    head_bottom = info.head.bottom
    eye_level = info.face.eyes.level
    eye_to_chin = head_bottom - eye_level
    head_height = head_bottom - head_top
    colors = [
        (255, 0, 0),
    ]
    color_index = 0

    original_image = image.copy()
    original_image_after_inital_cut = center_face_crop_x(image, info.face.center.x)
    # head_percentage = 50
    # eye_to_bottom_percentage = 56
    for head_percentage in range(50, 67, 3):
        for eye_to_bottom_percentage in range(56, 67, 3):
            image = original_image_after_inital_cut.copy()
            full_height = head_height / (head_percentage / 100)
            if full_height > image.shape[1]:
                print(f"Image ({file}):full height is bigger than image width")
                continue
            padding_percentage = 100 - head_percentage
            eye_to_chin_percentage = (eye_to_chin / head_height) * head_percentage
            bottom_padding_percentage = eye_to_bottom_percentage - eye_to_chin_percentage
            top_padding_percentage = padding_percentage - bottom_padding_percentage

            image_height = (head_height / head_percentage) * 100


            top_crop = head_top - (top_padding_percentage / 100 * image_height)
            bottom_crop = head_bottom + (bottom_padding_percentage / 100 * image_height)

            if top_padding_percentage < 0 or bottom_padding_percentage < 0:
                continue
            if top_padding_percentage < 5 or bottom_padding_percentage < 5:
                continue
            if top_crop < 0 or bottom_crop > image.shape[0]:
                continue


            cv2.line(image, (0, int(top_crop)), (int(image.shape[1]), int(top_crop)), colors[color_index], 8)
            cv2.putText(image, f"top padding: {top_padding_percentage:.2f}%", (0, int(top_crop)+100), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[color_index], 4, cv2.LINE_AA)
            cv2.line(image, (0, int(bottom_crop)), (int(image.shape[1]), int(bottom_crop)), colors[color_index], 8)
            cv2.putText(image, f"bottom padding: {bottom_padding_percentage:.2f}%", (0, int(bottom_crop)-50), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[color_index], 4, cv2.LINE_AA)

            cv2.line(image, (int((image.shape[1]/2) - (full_height/2)), int(top_crop)), (int((image.shape[1]/2) - (full_height/2)), int(bottom_crop)), colors[color_index], 8)
            cv2.line(image, (int((image.shape[1]/2) + (full_height/2)), int(top_crop)), (int((image.shape[1]/2) + (full_height/2)), int(bottom_crop)), colors[color_index], 8)

            cv2.line(image, (0, int(eye_level)), (int(image.shape[1]), int(eye_level)), colors[color_index], 8)
            cv2.putText(image, f"Face: {head_percentage}% \t Eye Level: {eye_to_bottom_percentage:.2f}%", (0, int(eye_level)- 50 * (color_index + 1)), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[color_index], 4, cv2.LINE_AA)

            # color_index += 1

            image_file_name = f"images/output/{file.split('.')[0]}_{head_percentage}_{eye_to_bottom_percentage}.jpg"
            cv2.imwrite(image_file_name, image)
    # image = cv2.resize(image, (int(image.shape[1]/4), int(image.shape[0]/4)))
    # cv2.imshow("image", image)
    # cv2.waitKey(0)

    # print(
    #     f"image height: {image_height} (100%)",
    #     f"head height: {head_height} ({head_percentage})%",
    #     f"top padding: {top_padding_percentage}%",
    #     f"bottom padding: {bottom_padding_percentage}%",
    #     f"top crop: {top_crop}",
    #     f"bottom crop: {bottom_crop}",
    #     sep="\n"
    # )


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# print(
#     f"Image(file):",
#     "\t",
#     "Face", "\t", "Glss", "\t", "Shldr", "\t", "Passed",
#     sep=""
# )
for file in sorted(os.listdir("images/input"), key=lambda x: int(x.split(".")[0])):
# for file in ["21.jpg"]:
    image = cv2.imread(f"images/input/{file}")
    with suppress_stdout():
        person = Person(image)
    if person.RESULTS.face.detected:
        # height = person.INFO.head.bottom - person.INFO.head.top
        # cv2.line(image, (0, int(person.INFO.head.top)), (int(image.shape[1]), int(person.INFO.head.top)), (0, 255, 0), 2)
        # cv2.line(image, (0, int(person.INFO.head.bottom + height*7/100)), (int(image.shape[1]), int(person.INFO.head.bottom + height*7/100)), (0, 255, 0), 2)

        # image = cv2.resize(image, (int(image.shape[1]/4), int(image.shape[0]/4)))

        # cv2.imshow("image", image)
        # cv2.waitKey(0)
        crop(file, image, person.INFO)


    # print(
    #     f"Image({file}):({person.INFO.head.top},{person.INFO.head.bottom})",
    #     "\t",
    #     "✅" if person.RESULTS.face.detected else "❌", "✅" if person.RESULTS.face.passed else "❌",
    #     "\t",
    #     "✅" if person.RESULTS.glasses.detected else "❌", "✅" if person.RESULTS.glasses.passed else "❌",
    #     "\t",
    #     "✅" if person.RESULTS.shoulders.detected else "❌", "✅" if person.RESULTS.shoulders.passed else "❌",
    #     "\t",
    #     "✅" if person.RESULTS.passed else "❌",
    #     sep=""
    # )




