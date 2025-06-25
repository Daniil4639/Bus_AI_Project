import cv2

from src.core.image_processor import ImageProcessor

def initialize_processor():
    processor = ImageProcessor()
    return processor

def analyze_image(processor, image_path):
    image = cv2.imread(image_path)
    warnings, image_with_boxes = processor(image)
    return warnings, image_with_boxes

# for name in images:
#     image = cv2.imread(name)

#     warnings, image_with_boxes = processor(image)
#     print(warnings)

#     if image_with_boxes is not None:
#         cv2.imshow('Detected_objects', image_with_boxes)
#         cv2.waitKey(0)
