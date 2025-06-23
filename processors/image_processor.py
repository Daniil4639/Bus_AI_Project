from detectors.object_detection import ObjectDetector, merge_dicts
from detectors.pose_detection import PoseDetector
from processors.output_image_processor import OutputImageProcessor
import processors.detection_exceptions as exceptions


# Процедура смещения зон предметов в руках
def shift_objects_boxes(detected_data, x_start, y_start):
    return {
        class_name: [
            [x1 + x_start, y1 + y_start, x2 + x_start, y2 + y_start]
            for x1, y1, x2, y2 in boxes
        ]
        for class_name, boxes in detected_data.items()
    }

# Процедура увеличения зоны рулевого колеса на 25%
def extend_wheel_rectangle_area(wheel_coord, img, start_point):
    x1, y1, x2, y2 = wheel_coord
    x1 += start_point
    x2 += start_point
    width, height, channels = img.shape

    wheel_width = x2 - x1
    wheel_height = y2 - y1
    extra_width = wheel_width / 4
    extra_height = wheel_height / 4

    width_to_left = round(min(x1, extra_width / 2))
    height_to_bottom = round(min(height - y2, extra_height / 2))
    width_to_right = round(min(width - x2, extra_width - width_to_left))
    height_to_top = round(min(y1, extra_height - height_to_bottom))

    return [x1 - width_to_left, y1 - height_to_top, x2 + width_to_right, y2 + height_to_bottom]

# Процедура изменения размеров изображения до квадратной формы (уменьшение длины)
def cut_image_to_square_by_driver_body(img, pose_landmarks):
    height, width, _ = img.shape

    left_top = int(pose_landmarks.landmark[12].x * width)
    left_bottom = int(pose_landmarks.landmark[24].x * width)
    right_top = int(pose_landmarks.landmark[11].x * width)
    right_bottom = int(pose_landmarks.landmark[23].x * width)

    avg_x = (left_top + left_bottom + right_top + right_bottom) // 4
    start_x = max(0, avg_x - height // 2)
    end_x = min(width, start_x + height)

    return img[:, start_x:end_x], start_x

# Процедура получения области 200 х 200 вокруг ключевой точки руки
def cut_area_around_hand(img, hand_landmark):
    img_height, img_width, _ = img.shape

    x_coord = int(hand_landmark.x * img_width)
    y_coord = int(hand_landmark.y * img_height)

    x_start = max(x_coord - 100, 0)
    x_end = min(img_width, x_start + 200)
    y_start = max(y_coord - 100, 0)
    y_end = min(img_height, y_start + 200)

    return img[y_start:y_end, x_start:x_end], x_start, y_start


# Класс, содержащий основной функционал модуля
class ImageProcessor(object):

    def __init__(self):
        self.pose_detector = PoseDetector()
        self.object_detector = ObjectDetector()
        self.output_processor = OutputImageProcessor()

    def __call__(self, image):
        try:
            return self.__process_image(image)
        except exceptions.NotDetectedException as ex:
            return [ex.message], None

    # Метод инициализации обработки изображения
    def __process_image(self, image):
        warning_list = []

        # Получение данных о позе
        pose_landmarks, left_hand_landmark, right_hand_landmark = self.__check_pose(image)

        # Обрезка фотографии до квадратного вокруг водителя
        squared_image_for_belt_and_wheel, start_point_squared_image_for_belt_and_wheel = (
            cut_image_to_square_by_driver_body(image, pose_landmarks))

        # Получение данных о ремне и рулевом колесе
        detected_data_wheel_and_belt = self.object_detector.detect_wheel_and_belt(squared_image_for_belt_and_wheel)

        # Проверка на наличие ремня безопасности
        try:
            self.__check_belt(detected_data_wheel_and_belt)
        except exceptions.NotDetectedException as ex:
            warning_list.append(ex.message)

        # Проверка рулевого колеса
        wheel_coordinates = self.__check_wheel(detected_data_wheel_and_belt, image,
                                               start_point_squared_image_for_belt_and_wheel)

        # Проверка рук на руле
        left_hand_on_the_wheel, right_hand_on_the_wheel = None, None
        try:
            left_hand_on_the_wheel, right_hand_on_the_wheel = self.__check_hands_on_wheel(
                left_hand_landmark, right_hand_landmark, wheel_coordinates, image)
        except exceptions.HandsAreNotOnWheelException as ex:
            warning_list.append(ex.message)

        # Проверка предметов в левой и правой руке
        image_with_boxes = self.__check_objects_in_hands(image, warning_list, left_hand_landmark, right_hand_landmark)

        return warning_list, image_with_boxes

    # Метод проверки обнаружения ремня безопасности
    def __check_belt(self, data):
        if 'belt' not in data:
            raise exceptions.NotDetectedException('Ремень не распознан. Возможно, водитель не пристегнут!')

    # Метод проверки обнаружения рулевого колеса, возвращает координаты
    def __check_wheel(self, data, img, start_point):
        if 'wheel' not in data:
            raise exceptions.NotDetectedException('Органы управления не распознаны!')

        return extend_wheel_rectangle_area(data['wheel'][0], img, start_point)

    # Метод проверки рук на рулевом колесе
    def __check_hands_on_wheel(self, left_hand_landmark, right_hand_landmark, wheel_coordinates, img):
        img_height, img_width, _ = img.shape

        left_hand_on_the_wheel, right_hand_on_the_wheel = False, False

        if wheel_coordinates[0] < left_hand_landmark.x * img_width < wheel_coordinates[2] and \
                wheel_coordinates[1] < left_hand_landmark.y * img_height < wheel_coordinates[3]:
            left_hand_on_the_wheel = True

        if wheel_coordinates[0] < right_hand_landmark.x * img_width < wheel_coordinates[2] and \
                wheel_coordinates[1] < right_hand_landmark.y * img_height < wheel_coordinates[3]:
            right_hand_on_the_wheel = True

        if not left_hand_on_the_wheel and not right_hand_on_the_wheel:
            raise exceptions.HandsAreNotOnWheelException('Возможно, водитель не держит руки на руле!')

        return left_hand_on_the_wheel, right_hand_on_the_wheel

    # Метод проверки обнаружения важных для дальнейшей обработки точек тела
    def __check_pose(self, img):
        result = self.pose_detector.get_pose_landmarks(img)

        if result is None:
            raise exceptions.NotDetectedException('Водитель не распознан!')

        if (result.landmark[11] is None) or (result.landmark[12] is None) or (result.landmark[23] is None) \
            or (result.landmark[14] is None):
            raise exceptions.NotDetectedException('Не распознан торс водителя!')

        left_hand, right_hand = self.pose_detector.get_hands_anchor_points(result.landmark)

        if (left_hand is None) or (right_hand is None):
            raise exceptions.NotDetectedException('Не распознаны руки водителя!')

        return result, left_hand, right_hand

    # Метод инициализации вызова метода обработки предметов в руках
    def __check_objects_in_hands(self, img, warnings, left_landmark, right_landmark):
        detected_data = {}

        try:
            self.__check_objects_in_hand(img, left_landmark, 'левой')
        except exceptions.ExtraObjectInHandsException as ex:
            warnings.append(ex.message)
            detected_data = merge_dicts(detected_data, ex.groups)

        try:
            self.__check_objects_in_hand(img, right_landmark, 'правой')
        except exceptions.ExtraObjectInHandsException as ex:
            warnings.append(ex.message)
            detected_data = merge_dicts(detected_data, ex.groups)

        if len(detected_data) == 0:
            return None

        return self.output_processor.create_bounding_boxes(img, detected_data)

    # Метод проверки рук на наличие в них предсказуемого YOLO объекта
    def __check_objects_in_hand(self, img, hand_landmark, hand_name):
        area_around_hand, x_start, y_start = cut_area_around_hand(img, hand_landmark)

        detected_data = self.object_detector.detect_object_in_hand(area_around_hand)
        detected_data.pop('person', None)
        detected_data.pop('motorcycle', None)
        detected_data.pop('toilet', None)
        detected_data.pop('waste', None)
        detected_data = shift_objects_boxes(detected_data, x_start, y_start)

        if len(detected_data) == 0:
            return

        raise exceptions.ExtraObjectInHandsException(
            'В ' + hand_name + ' руке обнаружен один из следующих объектов: ' + str(detected_data.keys()),
            detected_data)
