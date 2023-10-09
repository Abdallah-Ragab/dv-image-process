from .constants import *
import math

class Body:
    def __init__(self, *args, **kwargs):
        self.BODY = self.get_pose_landmarks()
        self.SHOULDERS = self.get_shoulders_position()

        super().__init__(*args, **kwargs)

    def get_pose_landmarks(self):
        try:
            return POSE.process(self.image).pose_landmarks
        except Exception as e:
            print(f"Could not detect pose landmarks: {e}")
            return None

    def get_shoulders_position(self):
        pose_index = POSE_SOLUTION.PoseLandmark
        try:
            left_shoulder = OBJ(
                x=self.BODY.landmark[pose_index.LEFT_SHOULDER].x * self.dimensions.x,
                y=self.BODY.landmark[pose_index.LEFT_SHOULDER].y * self.dimensions.y,
            )
            right_shoulder = OBJ(
                x=self.BODY.landmark[pose_index.RIGHT_SHOULDER].x * self.dimensions.x,
                y=self.BODY.landmark[pose_index.RIGHT_SHOULDER].y * self.dimensions.y,
            )
            shoulders = OBJ(
                left = left_shoulder,
                right = right_shoulder
            )
            return shoulders
        except Exception as e:
            print (f"Could not find shoulders position: {e}")
            return None

    def calculate_shoulders_slope(self):
        try:
            shoulders_distance = math.dist((self.SHOULDERS.left.x, self.SHOULDERS.left.y), (self.SHOULDERS.right.x, self.SHOULDERS.right.y))
            shoulders_y_diff = abs(self.SHOULDERS.right.y - self.SHOULDERS.left.y)

            angle = math.asin(shoulders_y_diff/shoulders_distance)
            shoulders_slope = math.degrees(angle)
            return shoulders_slope
        except Exception as e:
            print(f"Could not calculate shoulders slope: {e}")
            return None

    def get_body_info(self):
        try:
            return OBJ(
                # position = self.SHOULDERS,
                slope = self.calculate_shoulders_slope()
            )
        except Exception as e:
            print(f"Could not get shoulders info: {e}")
            return None

    def gather_info(self):
        try:
            setattr(self.INFO, "shoulders", self.get_body_info())
        except Exception as e:
            print(f"Could not gather info in {self.__class__.__name__}: {e}")
