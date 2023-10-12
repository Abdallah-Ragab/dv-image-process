import cv2
import mediapipe as mp
from log_config import logger

font = cv2.FONT_HERSHEY_SIMPLEX

blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)


POSE_SOLUTION = mp.solutions.pose
FACE_MECH_SOLUTION = mp.solutions.face_mesh
SELFIE_SEG_SOLUTION = mp.solutions.selfie_segmentation
DRAWING_SOLUTION = mp.solutions.drawing_utils

FACE_MECH = FACE_MECH_SOLUTION.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=True)
POSE = POSE_SOLUTION.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=True)
SELFIE_SEG = SELFIE_SEG_SOLUTION.SelfieSegmentation(model_selection=0)
DRAWING_SPEC = DRAWING_SOLUTION.DrawingSpec(thickness=1, circle_radius=1)


class OBJ:
    def __init__(self, **kwargs) -> None:
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def dict(self):
        dict_ = {}
        for key in self.__dict__:
            if isinstance(self.__dict__[key], OBJ):
                dict_[key] = self.__dict__[key].dict()
            else:
                dict_[key] = self.__dict__[key]
        return dict_

    def __repr__(self) -> str:
        return str(self.dict())
