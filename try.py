import cv2
from models import Person

image = cv2.imread("images/input/0.jpg")
person = Person(image)
print(person.INFO.dict())
print(person.INFO.head.top)
print(person.RESULTS.dict())
