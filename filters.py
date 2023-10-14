from models.constants import *
import numpy

BLUR_INTENSITY = 15

def blur(image, intensity=BLUR_INTENSITY):
    """
    Apply a blur filter to the input image.

    Args:
        image (numpy.ndarray): The input image.
        intensity (int): The intensity of the blur filter.

    Returns:
        numpy.ndarray: The blurred image.
    """
    if not isinstance(image, numpy.ndarray):
        raise TypeError("Input image must be a numpy.ndarray")
    if not isinstance(intensity, int):
        raise TypeError("Intensity must be an integer")
    if intensity < 1:
        raise ValueError("Intensity must be greater than 0")
    return cv2.blur(image, (intensity, intensity))
