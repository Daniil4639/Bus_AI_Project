"""
Система мониторинга IP камер

Веб-приложение для мониторинга IP камер с анализом видеопотока нейронными сетями.
Построено на FastAPI с использованием WebSocket для потоковой передачи видео.

Основные компоненты:
- camera_service: Обработка RTSP потока
- neural_service: Анализ кадров нейронной сетью
- database: Работа с PostgreSQL
- api: HTTP и WebSocket маршруты

Автор: RiddlerXenon
Дата создания: 2025-06-24
"""

__title__ = "Camera Monitoring System"
__version__ = "1.0.0"
__author__ = "RiddlerXenon"
__email__ = "riddler@example.com"
__description__ = "Система мониторинга IP камер с анализом нейронными сетями"

# Импорты для удобного использования
from app.config import settings
from app.utils.logger import logger

# Экспорт основных компонентов
__all__ = [
    "settings",
    "logger",
    "__version__",
    "__title__",
    "__author__",
    "__description__"
]
