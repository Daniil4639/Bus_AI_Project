wheel_and_belt_model_classes = ['wheel', 'belt']
bottles_model_classes = ['bottle', 'suspicious', 'waste']
base_model_classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
                      'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
                      'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
                      'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
                      'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
                      'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
                      'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',
                      'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
                      'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
                      'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
                      'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
                      'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
                      'scissors', 'teddy bear', 'hair drier', 'toothbrush']


# Процедура группировки обнаруженных объектов
def make_object_groups_for_cpu(data, classes_names, scale):
    grouped_objects = {}

    for det in data:
        x1, y1, x2, y2, _, cls = det
        x1, y1, x2, y2 = [int((elem * scale).round().item()) for elem in [x1, y1, x2, y2]]
        class_name = classes_names[int(cls.round().item())]

        if class_name not in grouped_objects:
            grouped_objects[class_name] = []
        grouped_objects[class_name].append([x1, y1, x2, y2])

    return grouped_objects