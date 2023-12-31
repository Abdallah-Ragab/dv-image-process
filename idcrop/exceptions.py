class CouldNotDetect(Exception):
    def __init__(self, object_name=None):
        message = f"Failed to detect {object_name or '.'}"
        super().__init__(message)

class ExhaustedSequence(Exception):
    def __init__(self, sequence_name=None):
        message = f"Sequence {sequence_name or ''} exhausted without finding a suitable crop."
        super().__init__(message)
class MaxAttemptsExceeded(Exception):
    def __init__(self, sequence_name=None):
        message = f"Maximum attempts exceeded for sequence (200) {sequence_name or ''}."
        super().__init__(message)
class ImageTooSlim(Exception):
    def __init__(self):
        message = f"The image is too slim to be cropped at the right dimensions (image width is too small)."
        super().__init__(message)

class HeadTooClose(Exception):
    def __init__(self):
        message = f"The head is too close to the top or bottom edges of the image."
        super().__init__(message)
class HeadTooHigh(Exception):
    def __init__(self):
        message = f"The The head is too close to the top edge of the image."
        super().__init__(message)

class SaveError(Exception):
    def __init__(self, reason=None):
        message = f"Saving Image Failed. {reason if reason else ''}"
        super().__init__(message)