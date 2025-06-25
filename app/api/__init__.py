"""
Пакет API приложения

Содержит HTTP и WebSocket маршруты для:
- REST API для управления камерой и получения данных
- WebSocket для потоковой передачи видео
- Обработку запросов и ответов

Основные модули:
- routes: HTTP маршруты REST API
- websocket: WebSocket обработчики для видеопотока

API Endpoints:
    HTTP:
    - GET /: Главная страница
    - GET /api/camera/status: Статус камеры
    - POST /api/camera/start: Запуск камеры
    - POST /api/camera/stop: Остановка камеры
    - GET /api/database/results: Данные из БД
    - GET /health: Проверка состояния системы
    
    WebSocket:
    - WS /ws/camera: Поток видео данных

Использование:
    from app.api import router
    
    app.include_router(router)
"""

from app.api.routes import router
from app.api.websocket import websocket_camera_handler

# Экспорт основных компонентов
__all__ = [
    "router",
    "websocket_camera_handler",
]

# Информация о пакете
__version__ = "1.0.0"
__description__ = "HTTP и WebSocket API для системы мониторинга камер"

# API настройки
API_VERSION = "v1"
API_PREFIX = "/api"

# Константы для API
HTTP_METHODS = {
    "GET": "GET",
    "POST": "POST", 
    "PUT": "PUT",
    "DELETE": "DELETE",
    "PATCH": "PATCH"
}

# Коды статусов HTTP
HTTP_STATUS_CODES = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503
}

# WebSocket коды
WEBSOCKET_CODES = {
    "NORMAL_CLOSURE": 1000,
    "GOING_AWAY": 1001,
    "PROTOCOL_ERROR": 1002,
    "UNSUPPORTED_DATA": 1003,
    "INVALID_FRAME_PAYLOAD_DATA": 1007,
    "POLICY_VIOLATION": 1008,
    "MESSAGE_TOO_BIG": 1009,
    "INTERNAL_ERROR": 1011
}

# Лимиты API
API_LIMITS = {
    "max_results_per_request": 1000,
    "max_file_size_mb": 100,
    "request_timeout_seconds": 30,
    "websocket_message_size_limit": 1024 * 1024 * 10  # 10MB
}

# Настройки CORS
CORS_SETTINGS = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}
