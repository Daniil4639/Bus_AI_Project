import os.path
from ultralytics import YOLO
import cv2

from src.utils import merge_dicts, make_object_groups


# Класс с методами поиска на изображении ожидаемых объектов
class ObjectDetector(object):

    def __init__(self):
        self.model_wheel_belt = YOLO(
            os.path.join(os.path.dirname(__file__), 'models', 'wheel_and_belt.pt'))
        self.base_model = YOLO(
            os.path.join(os.path.dirname(__file__), 'models', 'yolo11s.pt'))
        self.bottle_model = YOLO(
            os.path.join(os.path.dirname(__file__), 'models', 'bottle.pt'))

    # Метод поиска на изображении (BGR) ремня безопасности и рулевого колеса
    def detect_wheel_and_belt(self, img):
        input_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = self.model_wheel_belt(input_frame, imgsz=640)[0]

        return make_object_groups(results)

    # Метод поиска на изображении (BGR) телефона, чашки, бутылки
    def detect_object_in_hand(self, img):
        input_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results_1 = self.base_model(input_frame, imgsz=640, conf=0.5)[0]
        results_2 = self.bottle_model(input_frame, imgsz=640, conf=0.7)[0]

        return merge_dicts(make_object_groups(results_1), make_object_groups(results_2))
