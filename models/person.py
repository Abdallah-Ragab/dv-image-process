from .constants import *
from .face import Face
from .body import Body
from .head import Head

class Person(Face, Body, Head):
    INFO = OBJ()
    RESULTS = OBJ()
    def __init__(self, image):
        self.image = image
        self.dimensions = OBJ(x=image.shape[1], y=image.shape[0])
        self.face = self.get_face_landmarks()
        super().__init__()
        self.gather_info()
        self.determine_results()
    def gather_info(self):
        for base in __class__.__bases__:
            if hasattr(base, "gather_info"):
                base.gather_info(self)

    def determine_results(self):
        face_detected = bool(self.INFO.face.rotation)
        if face_detected and self.INFO.face.rotation.angles:
            face_rotation = (self.INFO.face.rotation.angles.x, self.INFO.face.rotation.angles.y, self.INFO.face.rotation.angles.z)
            glasses_detected = bool(self.INFO.face.glasses)

        shoulders_detected = bool(self.INFO.shoulders.slope)
        if shoulders_detected:
            shoulders_slope = self.INFO.shoulders.slope

        face_passed = (
            face_detected and
            abs(float(face_rotation[0])) < 2 and
            abs(float(face_rotation[1])) < 2 and
            abs(float(face_rotation[2])) < 2
        ) if face_detected else False

        glasses_passed = face_detected and not glasses_detected
        shoulders_passed = shoulders_detected and abs(float(shoulders_slope)) < 3
        passed = (face_passed and glasses_passed and shoulders_passed) if shoulders_detected else (face_passed and glasses_passed)

        face_results = OBJ(
            detected = face_detected,
            passed = face_passed
        )
        glasses_results = OBJ(
            detected = face_detected and glasses_detected,
            passed = glasses_passed
        )
        shoulders_results = OBJ(
            detected = shoulders_detected,
            passed = shoulders_passed
        )

        self.RESULTS = OBJ(
            face = face_results,
            glasses = glasses_results,
            shoulders = shoulders_results,
            passed = passed
        )

