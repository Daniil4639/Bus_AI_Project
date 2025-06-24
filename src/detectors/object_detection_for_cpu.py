import os
import numpy as np
import torch
from openvino.runtime import Core
import cv2
from ultralytics.utils import ops

from src.utils import merge_dicts, make_object_groups_for_cpu
from src.utils import wheel_and_belt_model_classes, base_model_classes, bottles_model_classes


# Класс с методами поиска на изображении ожидаемых объектов
class ObjectDetectorForCPU(object):

    def __init__(self):
        self.core = Core()
        self.model_wheel_belt = self.core.read_model(os.path.join(os.path.dirname(__file__), 'models_for_cpu', 'wheel_and_belt_openvino_model', 'wheel_and_belt.xml'))
        self.model_wheel_belt = self.core.compile_model(self.model_wheel_belt, 'CPU')

        self.base_model = self.core.read_model(os.path.join(os.path.dirname(__file__), 'models_for_cpu', 'yolo11s_openvino_model', 'yolo11s.xml'))
        self.base_model = self.core.compile_model(self.base_model, 'CPU')

        self.bottle_model = self.core.read_model(os.path.join(os.path.dirname(__file__), 'models_for_cpu', 'bottle_openvino_model', 'bottle.xml'))
        self.bottle_model = self.core.compile_model(self.bottle_model, 'CPU')

    # Метод поиска на изображении (BGR) ремня безопасности и рулевого колеса
    def detect_wheel_and_belt(self, img):
        original_h, _, _ = img.shape
        scale = original_h / 640.

        input_tensor = cv2.resize(img, (640, 640))
        input_tensor = input_tensor.transpose(2, 0, 1)[None]
        input_tensor = input_tensor.astype(np.float32) / 255.0

        outputs = self.model_wheel_belt(input_tensor)[0]

        predictions = ops.non_max_suppression(
            torch.from_numpy(outputs),
            nc=2
        )[0]

        return make_object_groups_for_cpu(predictions, wheel_and_belt_model_classes, scale)

    # Метод поиска на изображении (BGR) телефона, чашки, бутылки
    def detect_object_in_hand(self, img):
        original_h, _, _ = img.shape
        scale = original_h / 640.

        input_tensor = cv2.resize(img, (640, 640))
        input_tensor = input_tensor.transpose(2, 0, 1)[None]
        input_tensor = input_tensor.astype(np.float32) / 255.0

        outputs_1 = self.base_model(input_tensor)[0]
        outputs_2 = self.bottle_model(input_tensor)[0]

        predictions_1 = ops.non_max_suppression(
            torch.from_numpy(outputs_1),
            conf_thres=0.5,
            nc=80
        )[0]
        predictions_2 = ops.non_max_suppression(
            torch.from_numpy(outputs_2),
            conf_thres=0.7,
            nc=3
        )[0]

        return merge_dicts(make_object_groups_for_cpu(predictions_1, base_model_classes, scale),
                           make_object_groups_for_cpu(predictions_2, bottles_model_classes, scale))
