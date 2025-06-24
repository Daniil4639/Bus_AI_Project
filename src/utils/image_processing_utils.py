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