import cv2

from src.core.image_processor import ImageProcessor

processor = ImageProcessor()

# number = int(input())
# image = None
#
# if number == 1:
#     image = cv2.imread(r'photos/image_correct.png')
# elif number == 2:
#     image = cv2.imread(r'photos/image_without_belt.png')
# elif number == 3:
#     image = cv2.imread(r'photos/image_without_belt_and_with_bottle.png')
# elif number == 4:
#     image = cv2.imread(r'photos/image_with_phone.png')
# else:
#     image = cv2.imread(r'photos/image_correct.png')
#
# warnings, image_with_boxes = processor(image)
# print(warnings)
#
# if image_with_boxes is not None:
#     cv2.imshow('Detected_objects', image_with_boxes)
#     cv2.waitKey(0)

images = ['photos/image_correct.png', 'photos/image_without_belt.png',
          'photos/image_without_belt_and_with_bottle.png', 'photos/image_with_phone.png']

for name in images:
    image = cv2.imread(name)

    warnings, image_with_boxes = processor(image)
    print(warnings)

    if image_with_boxes is not None:
        cv2.imshow('Detected_objects', image_with_boxes)
        cv2.waitKey(0)
