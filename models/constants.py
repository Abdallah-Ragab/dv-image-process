import cv2
import mediapipe as mp

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
FACE_MECH = FACE_MECH_SOLUTION.FaceMesh(
    min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=True
)
DRAWING_SOLUTION = mp.solutions.drawing_utils
DRAWING_SPEC = DRAWING_SOLUTION.DrawingSpec(thickness=1, circle_radius=1)


class Object:
    def __init__(self, **kwargs) -> None:
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])