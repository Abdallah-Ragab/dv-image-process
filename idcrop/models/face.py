from .constants import *
from exceptions import CouldNotDetect
import numpy


class Face:
    FACES_COUNT = 0
    FACE_LANDMARK_INDEXES = [1, 33, 61, 199, 263, 291]
    NOSE_BRIDGE_LANDMARK_INDEXES = [
        9,
        8,
        168,
        6,
        197,
        195,
        417,
        351,
        419,
        412,
        413,
        464,
        357,
        193,
        122,
        196,
        188,
        189,
        245,
        188,
        174,
    ]
    def get_face_landmarks(self):
        try:
            logger.info(f"Getting face landmarks...")
            self.image.flags.writeable = False
            mesh = FACE_MECH.process(self.image)
            self.image.flags.writeable = True
            landmarks = mesh.multi_face_landmarks
            self.FACES_COUNT = len(landmarks)
            logger.success(f"Found {self.FACES_COUNT} faces.")
            return landmarks
        except Exception as e:
            logger.error(f"Failed to find face landmarks: {e.__traceback__.tb_lineno}:{e}")
            raise CouldNotDetect("face landmarks")

    def get_face_3d(self):
        try:
            logger.info(f"Getting face 3D position...")
            face_3d = numpy.array(
                [
                    [
                        landmark.x * self.dimensions.x,
                        landmark.y * self.dimensions.y,
                        landmark.z,
                    ]
                    for idx, landmark in enumerate(self.FACE[0].landmark)
                    if idx in self.FACE_LANDMARK_INDEXES
                ],
                dtype=numpy.float64,
            )
            logger.success(f"Face 3D position found successfully.")
            return face_3d

        except Exception as e:
            logger.error(f"Failed to find face 3D: {e.__traceback__.tb_lineno}:{e}")
            return None

    def get_face_2d(self):
        try:
            logger.info(f"Getting face 2D position...")
            face_2d = numpy.array(
                [
                    [landmark.x * self.dimensions.x, landmark.y * self.dimensions.y]
                    for idx, landmark in enumerate(self.FACE[0].landmark)
                    if idx in self.FACE_LANDMARK_INDEXES
                ],
                dtype=numpy.float64,
            )
            logger.success(f"Face 2D position found successfully.")
            return face_2d
        except Exception as e:
            logger.error(f"Failed to find face 2D: {e.__traceback__.tb_lineno}:{e}")
            return None

    def get_nose_bridge_position(self):
        try:
            logger.info(f"Getting nose bridge position...")
            nose_bridge = numpy.array(
                [
                    [landmark.x * self.dimensions.x, landmark.y * self.dimensions.y]
                    for idx, landmark in enumerate(self.FACE[0].landmark)
                    if idx in self.NOSE_BRIDGE_LANDMARK_INDEXES
                ],
                dtype=numpy.float64,
            )
            logger.success(f"Nose bridge position found successfully.")
            return nose_bridge
        except Exception as e:
            logger.error(f"Failed to find nose bridge position: {e.__traceback__.tb_lineno}:{e}")
            return None

    def get_eye_position(self):
        try:
            logger.info(f"Getting eye position...")
            eye = numpy.array(
                [
                    [landmark.x * self.dimensions.x, landmark.y * self.dimensions.y]
                    for idx, landmark in enumerate(self.FACE[0].landmark)
                    if idx in [133, 362]
                ],
                dtype=numpy.float64,
            )
            logger.success(f"Eye position found successfully.")
            return eye
        except Exception as e:
            logger.error(f"Failed to find eye position: {e.__traceback__.tb_lineno}:{e}")
            return None

    def get_eye_level(self):
        try:
            logger.info("Calculating eye level...")
            ys = self.EYES[:, 1]
            eye_level = (ys[0] + ys[1]) / 2
            logger.success(f"Eye level found: {eye_level}")
            return eye_level
        except Exception as e:
            logger.error(f"Failed to find eye level: {e.__traceback__.tb_lineno}:{e}")
            return None

    def get_face_center(self):
        logger.info("Calculating face center...")
        try:
            center = OBJ(
                x=self.FACE[0].landmark[1].x * self.dimensions.x,
                y=self.FACE[0].landmark[1].y * self.dimensions.y,
            )
            logger.success(f"Face center found: {center}")
            return center
        except Exception as e:
            logger.error(f"Failed to find face center: {e.__traceback__.tb_lineno}:{e}")
            return None

    def get_face_rotation(self):
        try:
            logger.info(f"Calculating face rotation...")
            focal_length = self.dimensions.x
            camera_center = (self.dimensions.x / 2, self.dimensions.y / 2)
            camera_matrix = numpy.array(
                [
                    [focal_length, 0, camera_center[0]],
                    [0, focal_length, camera_center[1]],
                    [0, 0, 1],
                ],
                dtype="double",
            )

            dist_coeffs = numpy.zeros((4, 1), dtype=numpy.float64)
            (success, rotation_vector, translation_vector) = cv2.solvePnP(
                self.FACE_3D,
                self.FACE_2D,
                camera_matrix,
                dist_coeffs,
            )
            rmat, jac = cv2.Rodrigues(rotation_vector)
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            rotational_angles = OBJ(
                x=angles[0] * 360,
                y=angles[1] * 360,
                z=angles[2] * 360,
            )
            if (
                rotational_angles.y < 2
                and rotational_angles.y > -2
                and rotational_angles.x < 2
                and rotational_angles.x > -2
            ):
                direction = "Forward"
            elif rotational_angles.y < -10:
                direction = "Left"
            elif rotational_angles.y > 10:
                direction = "Right"
            elif rotational_angles.x < -10:
                direction = "Down"
            elif rotational_angles.x > 10:
                direction = "Up"
            elif rotational_angles.y < -2:
                direction = "Slightly Left"
            elif rotational_angles.y > 2:
                direction = "Slightly Right"
            elif rotational_angles.x < -2:
                direction = "Slightly Down"
            elif rotational_angles.x > 2:
                direction = "Slightly Up"
            else:
                direction = None

            logger.success(f"Face direction found: {direction}")
            return OBJ(angles=rotational_angles, direction=direction, success=True)

        except Exception as e:
            logger.error(f"Failed to calculate face rotation: {e.__traceback__.tb_lineno}:{e}")
            return OBJ(success=False)

    def crop_nose_bridge_image(self):
        logger.info("Cropping nose bridge image...")
        try:
            x = self.NOSE_BRIDGE[:, 0]
            y = self.NOSE_BRIDGE[:, 1]
            x_min = int(x.min())
            x_max = int(x.max())
            y_min = int(y.min())
            y_max = int(y.max())
            cropped_image = self.image[y_min:y_max, x_min:x_max]
            logger.success("Nose bridge image cropped successfully.")
            return cropped_image
        except Exception as e:
            logger.error(f"Failed to crop nose bridge: {e.__traceback__.tb_lineno}:{e}")
            return None

    def detect_glasses(self):
        try:
            logger.info("Detecting glasses...")
            nose_bridge = self.crop_nose_bridge_image()
            img_blur = cv2.GaussianBlur(
                numpy.array(nose_bridge), (3, 3), sigmaX=0, sigmaY=0
            )
            edges = cv2.Canny(
                image=img_blur,
                threshold1=100,
                threshold2=210,
                apertureSize=3,
                L2gradient=True,
            )
            edges_center = edges.T[(int(len(edges.T) / 2))]

            if 255 in edges_center:
                logger.success("Glasses detected")
                return OBJ(success=True, detected=True)
            else:
                logger.success("No glasses detected")
                return OBJ(success=True, detected=False)
        except Exception as e:
            logger.error(f"Failed to detect glasses: {e.__traceback__.tb_lineno}:{e}")
            return OBJ(success=False)

    def get_face_info(self):
        try:
            logger.info(f"Getting face info...")
            self.FACE = self.get_face_landmarks()
            self.FACE_3D = self.get_face_3d()
            self.FACE_2D = self.get_face_2d()
            self.NOSE_BRIDGE = self.get_nose_bridge_position()
            self.EYES = self.get_eye_position()

            face_rotation = self.get_face_rotation()
            glasses_detection = self.detect_glasses()
            eye_level = self.get_eye_level()
            face_center = self.get_face_center()
            face_detected = bool(
                self.FACE is not None and
                self.FACE_2D is not None and
                self.FACE_3D is not None
            )

            logger.success(f"Face info found successfully.")
            return OBJ(
                success=face_detected,
                rotation=face_rotation,
                position=OBJ(_3D=self.FACE_3D, _2D=self.FACE_2D),
                count=self.FACES_COUNT,
                glasses=glasses_detection,
                eyes=OBJ(level=eye_level, position=self.EYES),
                center=face_center,
            )

        except CouldNotDetect as e:
            logger.error(f"Failed to get face info: {e.__traceback__.tb_lineno}:{e}")
            return OBJ(success=False, glasses=OBJ(success=False))

        except Exception as e:
            logger.error(f"Failed to get face info: {e.__traceback__.tb_lineno}:{e}")
            return OBJ(success=False, glasses=OBJ(success=False))

    def gather_info(self):
        try:
            setattr(self.INFO, "face", self.get_face_info())
        except Exception as e:
            logger.critical(f"Failed to gather info in {self.__class__.__name__}: {e.__traceback__.tb_lineno}:{e}")
