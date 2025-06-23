from src.detectors import *
from .output_image_processor import OutputImageProcessor
from src.exceptions import *
from src.utils import *


# Класс, содержащий основной функционал модуля
class ImageProcessor(object):

    def __init__(self):
        self.pose_detector = PoseDetector()
        self.object_detector = ObjectDetector()
        self.output_processor = OutputImageProcessor()

    def __call__(self, image):
        try:
            return self.__process_image(image)
        except NotDetectedException as ex:
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
        except NotDetectedException as ex:
            warning_list.append(ex.message)

        # Проверка рулевого колеса
        wheel_coordinates = self.__check_wheel(detected_data_wheel_and_belt, image,
                                               start_point_squared_image_for_belt_and_wheel)

        # Проверка рук на руле
        left_hand_on_the_wheel, right_hand_on_the_wheel = None, None
        try:
            left_hand_on_the_wheel, right_hand_on_the_wheel = self.__check_hands_on_wheel(
                left_hand_landmark, right_hand_landmark, wheel_coordinates, image)
        except HandsAreNotOnWheelException as ex:
            warning_list.append(ex.message)

        # Проверка предметов в левой и правой руке
        image_with_boxes = self.__check_objects_in_hands(image, warning_list, left_hand_landmark, right_hand_landmark)

        return warning_list, image_with_boxes

    # Метод проверки обнаружения ремня безопасности
    def __check_belt(self, data):
        if 'belt' not in data:
            raise NotDetectedException('Ремень не распознан. Возможно, водитель не пристегнут!')

    # Метод проверки обнаружения рулевого колеса, возвращает координаты
    def __check_wheel(self, data, img, start_point):
        if 'wheel' not in data:
            raise NotDetectedException('Органы управления не распознаны!')

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
            raise HandsAreNotOnWheelException('Возможно, водитель не держит руки на руле!')

        return left_hand_on_the_wheel, right_hand_on_the_wheel

    # Метод проверки обнаружения важных для дальнейшей обработки точек тела
    def __check_pose(self, img):
        result = self.pose_detector.get_pose_landmarks(img)

        if result is None:
            raise NotDetectedException('Водитель не распознан!')

        if (result.landmark[11] is None) or (result.landmark[12] is None) or (result.landmark[23] is None) \
            or (result.landmark[14] is None):
            raise NotDetectedException('Не распознан торс водителя!')

        left_hand, right_hand = self.pose_detector.get_hands_anchor_points(result.landmark)

        if (left_hand is None) or (right_hand is None):
            raise NotDetectedException('Не распознаны руки водителя!')

        return result, left_hand, right_hand

    # Метод инициализации вызова метода обработки предметов в руках
    def __check_objects_in_hands(self, img, warnings, left_landmark, right_landmark):
        detected_data = {}

        try:
            self.__check_objects_in_hand(img, left_landmark, 'левой')
        except ExtraObjectInHandsException as ex:
            warnings.append(ex.message)
            detected_data = merge_dicts(detected_data, ex.groups)

        try:
            self.__check_objects_in_hand(img, right_landmark, 'правой')
        except ExtraObjectInHandsException as ex:
            warnings.append(ex.message)
            detected_data = merge_dicts(detected_data, ex.groups)

        if len(detected_data) == 0:
            return None

        return self.output_processor(img, detected_data)

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

        raise ExtraObjectInHandsException(
            'В ' + hand_name + ' руке обнаружен один из следующих объектов: ' + str(detected_data.keys()),
            detected_data)
