import cv2
import numpy as np
import sqlalchemy as sa

from .db_config import postgresql as settings


def resize_image(image, max_height=640):
    h, w, _ = image.shape
    ratio = max_height / float(h)

    new_width = int(w * ratio)
    return cv2.resize(image, (new_width, max_height))

def encode_image(image):
    if image is None:
        return None

    _, img_encoded = cv2.imencode('.png', image)
    return img_encoded.tobytes()

def decode_image(image_data):
    if image_data is None:
        return None

    img_buffer = np.frombuffer(image_data, dtype=np.uint8)
    return cv2.imdecode(img_buffer, cv2.IMREAD_COLOR)

def get_engine_from_settings():
    keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
    if not all(key in keys for key in settings.keys()):
        raise Exception('Bad config file!')

    return __get_engine(
        settings['pguser'],
        settings['pgpasswd'],
        settings['pghost'],
        settings['pgport'],
        settings['pgdb']
    )


def __get_engine(user, password, host, port, db):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db}'

    return sa.create_engine(url)