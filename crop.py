from models.constants import *
import cv2, os
import numpy
from models import Person
from contextlib import contextmanager
import sys, os

class ExhaustedSequence(Exception):
    def __init__(self, sequence_name=None):
        message = f"Sequence {sequence_name or ''} exhausted without finding a suitable crop."
        super().__init__(message)
class Crop:
    def __init__(self, image, info):
        self.image = image
        self.dimensions = OBJ(x=image.shape[1], y=image.shape[0])
        self.info = info
        self.head_top = self.info.head.top
        self.head_bottom = self.info.head.bottom
        self.eye_level = self.info.face.eyes.level
        self.eye_to_chin = self.head_bottom - self.eye_level
        self.head_height = self.head_bottom - self.head_top
        self.head_error_margin = 5
        self.eye_error_margin = 3
        self.head_possible_ratios = range(50, 69 - self.head_error_margin, 1)
        self.eye_level_possible_ratios = range(56, 69 - self.eye_error_margin, 1)

    def calculate_crop_lines(self, head_percentage, eye_to_bottom_percentage):
        full_height = self.head_height / (head_percentage / 100)
        if full_height > self.dimensions.x:
            return
        padding_percentage = 100 - head_percentage
        eye_to_chin_percentage = (self.eye_to_chin / self.head_height) * head_percentage
        bottom_padding_percentage = eye_to_bottom_percentage - eye_to_chin_percentage
        top_padding_percentage = padding_percentage - bottom_padding_percentage

        image_height = (self.head_height / head_percentage) * 100

        top_crop = self.head_top - (top_padding_percentage / 100 * image_height)
        bottom_crop = self.head_bottom + (
            bottom_padding_percentage / 100 * image_height
        )

        if top_padding_percentage < 0 or bottom_padding_percentage < 0:
            return
        if top_padding_percentage < 5 or bottom_padding_percentage < 5:
            return
        if top_crop < 0 or bottom_crop > self.dimensions.y:
            return

        return OBJ(
            top=top_crop,
            bottom=bottom_crop,
            head_ratio=head_percentage,
            eye_level_ratio=eye_to_bottom_percentage,
            top_padding_ratio=top_padding_percentage,
            bottom_padding_ratio=bottom_padding_percentage,
            image_height=image_height,
        )

    def possible_crops_sequence(self):
        for head_percentage in self.head_possible_ratios:
            for eye_to_bottom_percentage in self.eye_level_possible_ratios:
                crop_lines = self.calculate_crop_lines(
                    head_percentage, eye_to_bottom_percentage
                )
                if crop_lines:
                    yield crop_lines

    def center_face_x(self, image, face_center, crop=False, draw=False):
        right_side = image.shape[1] - face_center
        left_side = face_center
        crop_size_side = min(right_side, left_side)
        crop_start = face_center - crop_size_side
        crop_end = face_center + crop_size_side
        if draw:
            cv2.line(
                image,
                (int(crop_start), 0),
                (int(crop_start), image.shape[0]),
                (0, 255, 0),
                2,
            )
            cv2.line(
                image,
                (int(crop_end), 0),
                (int(crop_end), image.shape[0]),
                (0, 255, 0),
                2,
            )
        if crop:
            return OBJ(
                image=image[:, int(crop_start) : int(crop_end)],
                start=crop_start,
                end=crop_end,
            )
        return OBJ(image=image, start=crop_start, end=crop_end)

    def elect_best_crop(self):
        preferred_head_ratio = 50
        preferred_eye_level_ratio = 60
        preferred_top_padding = 10

        preferred_head_ratio_idx = self.head_possible_ratios.index(preferred_head_ratio)
        preferred_eye_level_ratio_idx = self.eye_level_possible_ratios.index(
            preferred_eye_level_ratio
        )

        head_ratio_sequence = self.ratio_seq_generator(
            self.head_possible_ratios, preferred_head_ratio_idx
        )
        try:
            for head_ratio in head_ratio_sequence:
                eye_ratio_sequence = self.ratio_seq_generator(self.eye_level_possible_ratios, preferred_eye_level_ratio_idx, repeat=True)
                head_ratio_crops = {}
                eye_ratio = next(eye_ratio_sequence)
                direction = 1
                while len(head_ratio_crops) < len(self.eye_level_possible_ratios):
                    try:
                        if eye_ratio in head_ratio_crops:
                            eye_ratio = eye_ratio_sequence.send(direction)
                            print("skipped")
                            continue
                        crop = self.calculate_crop_lines(head_ratio, eye_ratio)
                        print(
                            f"  Ran a crop calculation for head_ratio={head_ratio}, eye_ratio={eye_ratio}. Crop: {crop.dict() if crop else None}"
                        )

                        head_ratio_crops[eye_ratio] = crop
                        if not crop:
                            eye_ratio = eye_ratio_sequence.send(direction)
                            continue

                        crops_over_padded = [
                            head_ratio_crops[ratio]
                            for ratio in head_ratio_crops
                            if head_ratio_crops[ratio] and head_ratio_crops[ratio].top_padding_ratio >= preferred_top_padding
                        ]
                        crops_under_padded = [
                            head_ratio_crops[ratio]
                            for ratio in head_ratio_crops
                            if head_ratio_crops[ratio] and head_ratio_crops[ratio].top_padding_ratio <= preferred_top_padding
                        ]

                        if crop.top_padding_ratio == preferred_top_padding:
                            return crop

                        if len(crops_over_padded) > 0 and len(crops_under_padded) > 0:
                            over_padded = crops_over_padded[0]
                            under_padded = crops_under_padded[0]

                            over_padded_diff = abs(
                                over_padded.top_padding_ratio - preferred_top_padding
                            )
                            under_padded_diff = abs(
                                under_padded.top_padding_ratio - preferred_top_padding
                            )
                            if over_padded_diff < under_padded_diff:
                                return over_padded
                            else:
                                return under_padded

                        if crop.top_padding_ratio > preferred_top_padding:
                            direction = -1
                        else:
                            direction = 1
                        eye_ratio = eye_ratio_sequence.send(direction)
                    except (ExhaustedSequence, StopIteration):
                        break

        except (ExhaustedSequence, StopIteration):
            pass

        return None

    def crop(self):
        image = self.center_face_x(self.image, self.info.face.center.x, crop=True).image
        crop_lines = self.elect_best_crop()
        if not crop_lines:
            return image
        else:
            image_height = crop_lines.bottom - crop_lines.top
            cropped_image = image[
                int(crop_lines.top) : int(crop_lines.bottom),
                int(image.shape[1] / 2 - image_height / 2) : int(image.shape[1] / 2 + image_height / 2)
            ]
            return cropped_image

    def ratio_seq_generator(self, input_list, start=None, repeat=False):
        index = start if start is not None else 0
        while True:
            if repeat:
                index = index % len(input_list)
            if index < len(input_list) and (index >= 0):
                step = yield input_list[index]
            else:
                raise ExhaustedSequence
            _step = step if step is not None and isinstance(step, int) else 1
            index += _step

# def ratio_seq_generator(input_list, start=None):
#     index = start if start is not None else 0
#     while True:
#         if index < len(input_list) and index >= 0:
#             step = yield input_list[index]
#         else:
#             raise StopIteration
#         _step = step if step is not None and isinstance(step, int) else 1
#         index += _step

# my_list = [1,2,3,4,5,6,7,8,9,10]
# seq = ratio_seq_generator(my_list, 4)
# printed = []
# counter = 0
# direction = 1
# val = next(seq)
# while counter < len(my_list):
#     counter += 1
#     if val in printed:
#         val = seq.send(direction)
#         print("skipped")
#         continue
#     printed.append(val)
#     print(val)
#     if val > 5:
#         direction = -1
#     elif val < 5:
#         direction = 1
#     val = seq.send(direction)
