import random
import cv2


# Класс с методами выделения областей на изображении и записи в директорию "output"
class OutputImageProcessor(object):

    def __init__(self):
        self.colors = colors = [
            (255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255), (0, 255, 255),
            (255, 255, 0), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
            (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
            (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
        ]

    # Метод отрисовки рамок
    def __call__(self, image, data):
        for class_name in data:
            color = self.colors[random.randint(0, len(self.colors) - 1)]

            for box in data[class_name]:
                x1, y1, x2, y2 = box
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return image
