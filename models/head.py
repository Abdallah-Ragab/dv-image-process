from .constants import *
import numpy

BG_COLOR = (192, 192, 192) # gray
MASK_COLOR = (255, 255, 255) # white

class Head:
    def __init__(self, *args, **kwargs):
        # self.info = self.get_head_info()
        self.PERSON_MASK = self.get_person_segmentation()

        super().__init__(*args, **kwargs)

    def get_person_segmentation(self):
        try:
            image = self.image
            image.flags.writeable = False
            person_seg = SELFIE_SEG.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            mask = person_seg.segmentation_mask.astype('uint8')

            return mask
        except Exception as e:
            print(f"Could not get person segmentation mask: {e}")
            return None

    def get_top_of_head(self):
        try:
            mask = self.PERSON_MASK
            top_of_head = numpy.where(mask == 1)
            top_of_head = top_of_head[0].min()
            return top_of_head
        except Exception as e:
            print(f"Could not get top of head: {e}")
            return None

    def get_head_info(self):
        try:
            top_of_head = self.get_top_of_head()
            head_info = Object(top=top_of_head)
            return head_info
        except Exception as e:
            print(f"Could not get head info: {e}")
            return None

    def gather_info(self):
        try:
            setattr(self.INFO, "head", self.get_head_info())
        except Exception as e:
            print(f"Could not gather info in {self.__class__.__name__}: {e}")
