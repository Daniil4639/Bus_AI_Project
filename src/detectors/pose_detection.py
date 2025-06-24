import cv2
from mediapipe.python.solutions import pose as mp_pose

# Класс с методами обработки позы на изображении
class PoseDetector(object):

    def __init__(self):
        self.pose_tracker = mp_pose.Pose(model_complexity=2, static_image_mode=True)
        self.left_hand_points = [19, 17, 15]
        self.right_hand_points = [20, 18, 16]

    # Получить координаты ключевых точек по изображению (BGR)
    def get_pose_landmarks(self, img):
        input_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.pose_tracker.process(image=input_frame)
        return result.pose_landmarks

    # Получить ключевые точки рук (по одной на руку для выделения зоны вокруг руки)
    def get_hands_anchor_points(self, landmarks):
        left_hand, right_hand = None, None

        for point in self.left_hand_points:
            if landmarks[point] is not None:
                left_hand = landmarks[point]
                break

        for point in self.right_hand_points:
            if landmarks[point] is not None:
                right_hand = landmarks[point]
                break

        return left_hand, right_hand
