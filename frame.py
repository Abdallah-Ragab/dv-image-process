from models.constants import *
from models import Face, Glasses, Shoulders

class Frame:
    def __init__(self, path):
        self.image = cv2.imread(path)
        self.process()
        self.info = self.gather_info()

    def process(self):
        self.face = Face(self.image)
        self.glasses = Glasses(self.image)
        self.shoulders = Shoulders(self.image)

    def gather_info(self):
        info = {}
        face_info = self.face.info
        glasses_info = self.glasses.info
        shoulders_info = self.shoulders.info


        info["face_detected"] = bool(face_info.rotation)
        if info['face_detected'] and face_info.rotation.angles:
            info['face_rotation'] = (face_info.rotation.angles.x, face_info.rotation.angles.y, face_info.rotation.angles.z)
            info['face_direction'] = face_info.rotation.direction
            info["glasses_detected"] = bool(glasses_info.glasses)

        info["shoulders_detected"] = bool(shoulders_info.slope)
        if info['shoulders_detected']:
            info['shoulders_slope'] = shoulders_info.slope

        info ['face_passed'] = (
            info['face_detected'] and
            abs(float(info['face_rotation'][0])) < 2 and
            abs(float(info['face_rotation'][1])) < 2 and
            abs(float(info['face_rotation'][2])) < 2
        )
        info ['glasses_passed'] = info['face_detected'] and not info['glasses_detected']
        info ['shoulders_passed'] = info['shoulders_detected'] and abs(float(info['shoulders_slope'])) > 3
        info ['passed'] = info['face_passed'] and info['glasses_passed'] and info['shoulders_passed'] if info['shoulders_detected'] else info['face_passed'] and info['glasses_passed']

        return info