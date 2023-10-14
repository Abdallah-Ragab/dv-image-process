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
        self.gather_info()
        self.determine_results()

    def gather_info(self):
        for base in __class__.__bases__:
            if hasattr(base, "gather_info"):
                base.gather_info(self)

    def determine_results(self):
        face_passed = self.face_passed()
        glasses_passed = self.glasses_passed()
        shoulders_passed = self.shoulders_passed()
        errors = self.get_errors()

        if self.INFO.shoulders.success:
            passed = (face_passed and glasses_passed and shoulders_passed)
        else:
            passed = (face_passed and glasses_passed)

        self.RESULTS = OBJ(
            passed = passed,
            face = OBJ(passed = face_passed, detected = self.INFO.face.success),
            glasses = OBJ(passed = glasses_passed, detected = self.INFO.face.glasses.success),
            shoulders = OBJ(passed = shoulders_passed, detected = self.INFO.shoulders.success),
            errors = errors
        )

    def face_passed(self):
        if self.INFO.face.success and self.INFO.face.rotation.success:
            return (
                self.INFO.face.success
                and abs(float(self.INFO.face.rotation.angles.x)) < 2
                and abs(float(self.INFO.face.rotation.angles.y)) < 2
                and abs(float(self.INFO.face.rotation.angles.z)) < 2
            )
        else:
            return False

    def glasses_passed(self):
        if self.INFO.face.success and self.INFO.face.glasses.success:
            return (
                self.INFO.face.success
                and self.INFO.face.glasses.success
                and not self.INFO.face.glasses.detected
            )
        else:
            return False

    def shoulders_passed(self):
        if self.INFO.shoulders.success:
            shoulders_slope = self.INFO.shoulders.slope or 999
            return abs(float(shoulders_slope)) < 3
        else:
            return False

    def get_errors(self):
        errors = []
        if not self.RESULTS.face.detected:
            errors.append({
                "code" : "NO_FACE",
                "message" : "Could not detect a face in the image. Try removing any obstructions and try again."
            })
        if not self.RESULTS.face.passed:
            errors.append({
                "code" : "FACE_NOT_STRAIGHT",
                "message" : "You are not looking straight at the camera. Please try again."
            })
        if not self.RESULTS.glasses.passed:
            errors.append({
                "code" : "GLASSES",
                "message" : "Glasses detected. Please remove your glasses and try again."
            })
        if not self.RESULTS.shoulders.passed:
            errors.append({
                "code" : "SHOULDERS",
                "message" : "You are not facing the camera. Try standing straight and facing the camera."
            })
        return errors