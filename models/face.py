from .constants import *
import numpy


class Face:
    number_of_faces = 0
    def __init__(self, image):
        self.image = image
        self.dimensions = Object(x=image.shape[1], y=image.shape[0])
        self.info = self.get_head_info()

    def get_face_landmarks(self):
        try:
            self.image.flags.writeable = False
            mesh = FACE_MECH.process(self.image)
            self.image.flags.writeable = True
            landmarks = mesh.multi_face_landmarks
            return landmarks
        except Exception as e:
            print(f"Could not find face landmarks: {e}")
            return None

    def get_face_position(self):
        try:
            landmarks = self.get_face_landmarks()
            self.number_of_faces = len(landmarks)
            face_3d = numpy.array(
                [
                    [
                        landmark.x * self.dimensions.x,
                        landmark.y * self.dimensions.y,
                        landmark.z,
                    ]
                    for idx, landmark in enumerate(landmarks[0].landmark)
                    if idx in [1, 33, 61, 199, 263, 291]
                ],
                dtype=numpy.float64,
            )
            face_2d = numpy.array(
                [
                    [landmark.x * self.dimensions.x, landmark.y * self.dimensions.y]
                    for idx, landmark in enumerate(landmarks[0].landmark)
                    if idx in [1, 33, 61, 199, 263, 291]
                ],
                dtype=numpy.float64,
            )

            return Object(_3D=face_3d, _2D=face_2d)

        except Exception as e:
            print(f"Could not find face position: {e}")
            return None

    def get_face_rotation(self):
        try:
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
                self.face._3D,
                self.face._2D,
                camera_matrix,
                dist_coeffs,
            )
            rmat, jac = cv2.Rodrigues(rotation_vector)
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            rotational_angles = Object(
                x=angles[0] * 360,
                y=angles[1] * 360,
                z=angles[2] * 360,
            )
            if rotational_angles.y < 2 and rotational_angles.y > -2 and rotational_angles.x < 2 and rotational_angles.x > -2:
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

            return Object(angles=rotational_angles, direction=direction)

        except Exception as e:
            print(f"Could not find face rotation: {e}")
            return None
    def get_head_info(self):
        self.face = self.get_face_position()
        self.rotation = self.get_face_rotation()
        return Object(position=self.face, rotation=self.rotation, count=self.number_of_faces)