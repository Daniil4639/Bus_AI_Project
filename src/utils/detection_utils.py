import numpy as np
from collections import defaultdict


# Процедура группировки обнаруженных объектов
def make_object_groups(data):
    classes_names = data.names
    classes = data.boxes.cls.cpu().numpy()
    boxes = data.boxes.xyxy.cpu().numpy().astype(np.int32)

    grouped_objects = {}

    for class_id, box in zip(classes, boxes):
        class_name = classes_names[int(class_id)]
        if class_name not in grouped_objects:
            grouped_objects[class_name] = []
        grouped_objects[class_name].append(box)

    return grouped_objects


# Процедура слияния двух словарей
def merge_dicts(dict1, dict2):
    result = defaultdict(list)

    for key, value in dict1.items():
        result[key].extend(value)

    for key, value in dict2.items():
        result[key].extend(value)

    return dict(result)