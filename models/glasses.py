from .constants import *
import numpy
class Glasses:
    NOSE_BRIDGE_LANDMARK_INDEXES = [
        9, 8, 168, 6, 197, 195, # Middle of nose bridge
        417, 351, 419, 412, # Right side of nose bridge
        413, 464, 357, # Right side of nose bridge
        193, 122, 196, 188, # Left side of nose bridge
        189, 245, 188, 174 # Left side of nose bridge
    ]

    def __init__(self, image):
        self.image = image
        self.dimensions = Object(x=image.shape[1], y=image.shape[0])
        self.info = self.get_info()

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
    def get_nose_bridge_position(self):
        landmarks = self.get_face_landmarks()
        try:
            nose_bridge = numpy.array(
                [
                    [landmark.x * self.dimensions.x, landmark.y * self.dimensions.y]
                    for idx, landmark in enumerate(landmarks[0].landmark)
                    if idx in self.NOSE_BRIDGE_LANDMARK_INDEXES
                ],
                dtype=numpy.float64,
            )
            return nose_bridge
        except Exception as e:
            print(f"Could not find nose bridge position: {e}")
            return None
    def crop_nose_bridge_image(self):
        try:
            nose_bridge = self.get_nose_bridge_position()
            x = nose_bridge[:, 0]
            y = nose_bridge[:, 1]
            x_min = int(x.min())
            x_max = int(x.max())
            y_min = int(y.min())
            y_max = int(y.max())
            cropped_image = self.image[y_min:y_max, x_min:x_max]
            return cropped_image
        except Exception as e:
            print(f"Could not crop nose bridge: {e}")
            return None
    def detect_glasses(self):
        try:
            nose_bridge = self.crop_nose_bridge_image()
            img_blur = cv2.GaussianBlur(numpy.array(nose_bridge),(3,3), sigmaX=0, sigmaY=0)
            edges = cv2.Canny(image = img_blur, threshold1=100, threshold2=210, apertureSize=3, L2gradient=True)
            edges_center = edges.T[(int(len(edges.T)/2))]

            if 255 in edges_center:
                return True
            else:
                return False
        except Exception as e:
            print(f"Could not detect glasses: {e}")
            return None

    def get_info(self):
        try:
            glasses_detected = self.detect_glasses()
            return Object(glasses=glasses_detected)
        except Exception as e:
            print(f"Could not get glasses info: {e}")
            return None