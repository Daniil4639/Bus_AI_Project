import os
from typing import Union
import cv2
import numpy as np
import json
from datetime import datetime

from app.config import settings

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_frame(frame: np.ndarray, prefix: str = "frame") -> str:
    """
    Сохраняет кадр в папке frames и возвращает путь до файла.
    """
    ensure_dir(settings.frames_dir)
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    filepath = os.path.join(settings.frames_dir, filename)
    cv2.imwrite(filepath, frame)
    return filepath

def save_result(result: Union[np.ndarray, dict], prefix: str = "result") -> str:
    """
    Сохраняет результат обработки (картинку или json) в папке results.
    """
    ensure_dir(settings.results_dir)
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    if isinstance(result, np.ndarray):
        filepath = os.path.join(settings.results_dir, filename + ".jpg")
        cv2.imwrite(filepath, result)
    elif isinstance(result, dict):
        filepath = os.path.join(settings.results_dir, filename + ".json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError("Результат должен быть np.ndarray или dict")
    return filepath
