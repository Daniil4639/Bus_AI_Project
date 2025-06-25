"""
Пакет сервисов приложения

Содержит бизнес-логику для:
- Работы с IP камерами и RTSP потоками
- Обработки видео нейронными сетями
- Утилит для асинхронной работы

Основные сервисы:
- CameraService: Управление камерой и видеопотоком
- NeuralNetworkService: Анализ кадров нейронной сетью
- Utils: Вспомогательные функции и декораторы

Архитектура:
    CameraService получает кадры -> NeuralNetworkService анализирует -> 
    результаты сохраняются в базу данных

Использование:
    from app.services import camera_service, neural_service
    
    # Запуск камеры
    await camera_service.start_streaming()
    
    # Обработка кадра
    results = await neural_service.process_frame(frame)
"""

from app.services.camera_service import CameraService, camera_service
from app.services.neural_service import NeuralNetworkService, neural_service
from app.services.utils import (
    async_retry,
    measure_time,
    AsyncContextManager,
    format_bytes,
    format_duration
)

# Экспорт основных компонентов
__all__ = [
    # Сервисы
    "CameraService",
    "camera_service",
    "NeuralNetworkService", 
    "neural_service",
    
    # Утилиты
    "async_retry",
    "measure_time",
    "AsyncContextManager",
    "format_bytes",
    "format_duration",
]

# Информация о пакете
__version__ = "1.0.0"
__description__ = "Сервисы для работы с камерой и нейронными сетями"

# Константы сервисов
CAMERA_RECONNECT_ATTEMPTS = 5
CAMERA_RECONNECT_DELAY = 3.0

NEURAL_MODEL_TYPES = [
    "person", "car", "bicycle", "motorcycle", "bus", "truck",
    "traffic_light", "stop_sign", "dog", "cat", "bird"
]

# Настройки производительности
PERFORMANCE_SETTINGS = {
    "max_frame_buffer": 10,
    "max_websocket_connections": 50,
    "frame_skip_threshold": 5,
    "memory_limit_mb": 512
}

# Статусы сервисов
SERVICE_STATUS = {
    "INITIALIZING": "initializing",
    "RUNNING": "running", 
    "STOPPED": "stopped",
    "ERROR": "error",
    "RECONNECTING": "reconnecting"
}
