from .constants import *
import math
from log_config import logger
from exceptions import CouldNotDetect


class Body:
    def get_pose_landmarks(self):
        try:
            logger.info(f"Getting pose landmarks...")
            return POSE.process(self.image).pose_landmarks
        except Exception as e:
            raise CouldNotDetect("pose landmarks")

    def get_shoulders_position(self):
        pose_index = POSE_SOLUTION.PoseLandmark
        try:
            logger.info(f"Getting shoulders position...")
            left_shoulder = OBJ(
                x=self.BODY.landmark[pose_index.LEFT_SHOULDER].x * self.dimensions.x,
                y=self.BODY.landmark[pose_index.LEFT_SHOULDER].y * self.dimensions.y,
            )
            right_shoulder = OBJ(
                x=self.BODY.landmark[pose_index.RIGHT_SHOULDER].x * self.dimensions.x,
                y=self.BODY.landmark[pose_index.RIGHT_SHOULDER].y * self.dimensions.y,
            )
            return OBJ(
                success = True,
                left = left_shoulder,
                right = right_shoulder
            )
        except Exception as e:
            logger.error(f"Could not find shoulders position: {e}")
            return OBJ(success=False)

    def calculate_shoulders_slope(self):
        try:
            logger.info(f"Calculating shoulders slope...")
            shoulders_distance = math.dist((self.SHOULDERS.left.x, self.SHOULDERS.left.y), (self.SHOULDERS.right.x, self.SHOULDERS.right.y))
            shoulders_y_diff = abs(self.SHOULDERS.right.y - self.SHOULDERS.left.y)

            angle = math.asin(shoulders_y_diff/shoulders_distance)
            shoulders_slope = math.degrees(angle)
            return shoulders_slope
        except Exception as e:
            logger.error(f"Could not calculate shoulders slope: {e}")
            return None

    def get_body_info(self):
        try:
            logger.info(f"Getting body info...")
            self.BODY = self.get_pose_landmarks()
            self.SHOULDERS = self.get_shoulders_position()
            shoulders_slope = self.calculate_shoulders_slope()
            return OBJ(
                success = self.SHOULDERS.success,
                position = self.SHOULDERS,
                slope = shoulders_slope
            )
        except CouldNotDetect as e:
            logger.error(f"Could not get body info: {e}")
            return None
        except Exception as e:
            logger.error(f"Could not get body info: {e}")
            return None

    def gather_info(self):
        try:
            setattr(self.INFO, "shoulders", self.get_body_info())
        except Exception as e:
            logger.critical(f"Could not gather info in {self.__class__.__name__}: {e}")
