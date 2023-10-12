from .constants import *
from exceptions import CouldNotDetect
import numpy

BG_COLOR = (192, 192, 192) # gray
MASK_COLOR = (255, 255, 255) # white

class Head:
    def get_person_segmentation(self):
        try:
            logger.info(f"Getting person segmentation mask...")
            image = self.image
            image.flags.writeable = False
            person_seg = SELFIE_SEG.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            mask = person_seg.segmentation_mask.astype('uint8')

            return mask
        except Exception as e:
            raise CouldNotDetect("person segmentation mask")

    def get_top_of_head(self):
        try:
            logger.info(f"Getting top of head position...")
            mask = self.PERSON_MASK
            top_of_head = numpy.where(mask == 1)
            top_of_head = top_of_head[0].min()
            return top_of_head
        except Exception as e:
            logger.error(f"Could not get top of head: {e}")
            return None

    def get_bottom_of_head(self):
        try:
            logger.info(f"Getting bottom of head position...")
            y_values = self.FACE_2D[:, 1]
            return numpy.max(y_values)
        except Exception as e:
            logger.error(f"Could not get bottom of head: {e}")
            return None

    def get_head_info(self):
        try:
            logger.info(f"Getting head info...")
            self.PERSON_MASK = self.get_person_segmentation()
            top_of_head = self.get_top_of_head()
            bottom_of_head = self.get_bottom_of_head()
            head_info = OBJ(top=top_of_head, bottom=bottom_of_head, success=True)
            return head_info
        except CouldNotDetect as e:
            logger.error(f"Could not get head info: {e}")
            return OBJ(success=False)
        except Exception as e:
            logger.error(f"Could not get head info: {e}")
            return OBJ(success=False)

    def gather_info(self):
        try:
            setattr(self.INFO, "head", self.get_head_info())
        except Exception as e:
            logger.critical(f"Could not gather info in {self.__class__.__name__}: {e}")
