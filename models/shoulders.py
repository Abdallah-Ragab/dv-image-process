from .constants import *
import math

class Shoulders:

    def __init__(self, image):
        self.image = image
        self.dimensions = Object(x=image.shape[1], y=image.shape[0])
        self.info = self.get_shoulders_info()

    def get_pose_landmarks(self):
        pose = POSE_SOLUTION.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=True
        )
        try:
            return pose.process(self.image).pose_landmarks
        except Exception as e:
            print(f"Could not detect pose landmarks: {e}")
            return None

    def get_shoulders_position(self):
        pose_index = POSE_SOLUTION.PoseLandmark
        try:
            landmarks = self.get_pose_landmarks()
            left_shoulder = Object(
                x=landmarks.landmark[pose_index.LEFT_SHOULDER].x * self.dimensions.x,
                y=landmarks.landmark[pose_index.LEFT_SHOULDER].y * self.dimensions.y,
            )
            right_shoulder = Object(
                x=landmarks.landmark[pose_index.RIGHT_SHOULDER].x * self.dimensions.x,
                y=landmarks.landmark[pose_index.RIGHT_SHOULDER].y * self.dimensions.y,
            )
            shoulders = Object(
                left = left_shoulder,
                right = right_shoulder
            )
            return shoulders
        except Exception as e:
            print (f"Could not find shoulders position: {e}")
            return None

    def get_shoulders_slope(self):
        try:
            shoulders_distance = math.dist((self.shoulders.left.x, self.shoulders.left.y), (self.shoulders.right.x, self.shoulders.right.y))
            shoulders_y_diff = abs(self.shoulders.right.y - self.shoulders.left.y)

            angle = math.asin(shoulders_y_diff/shoulders_distance)
            shoulders_slope = math.degrees(angle)
            return shoulders_slope
        except Exception as e:
            print(f"Could not calculate shoulders slope: {e}")
            return None


    def get_shoulders_info(self):
        try:
            self.shoulders = self.get_shoulders_position()
            self.shoulders_slope = self.get_shoulders_slope()
            return Object(
                position = self.shoulders,
                slope = self.shoulders_slope
            )
        except Exception as e:
            print(f"Could not get shoulders info: {e}")
            return None