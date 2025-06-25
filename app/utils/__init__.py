"""
Пакет утилит приложения

Содержит вспомогательные модули для:
- Логирования с настройкой уровней и форматирования
- Общих утилит для работы с файлами, временем, форматированием

Основные модули:
- logger: Настройка и управление логированием
- helpers: Вспомогательные функции (будущее расширение)

Логирование:
    Поддерживает различные уровни логирования:
    - DEBUG: Детальная отладочная информация
    - INFO: Общая информация о работе приложения
    - WARNING: Предупреждения о потенциальных проблемах
    - ERROR: Ошибки, которые не останавливают работу
    - CRITICAL: Критические ошибки

Использование:
    from app.utils import logger
    
    logger.info("Приложение запущено")
    logger.error("Ошибка подключения к камере")
    logger.debug("Детальная информация для отладки")
"""

from app.utils.logger import setup_logger, logger

# Экспорт основных компонентов
__all__ = [
    "setup_logger",
    "logger",
]

# Информация о пакете
__version__ = "1.0.0"
__description__ = "Утилиты для логирования и вспомогательных функций"

# Константы для логирования
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

LOG_FORMATS = {
    "simple": "%(levelname)s - %(message)s",
    "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "json": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
}

# Настройки логирования по умолчанию
DEFAULT_LOG_CONFIG = {
    "level": "INFO",
    "format": "detailed",
    "file_rotation": True,
    "max_file_size": "10MB",
    "backup_count": 5
}

# Категории логов
LOG_CATEGORIES = {
    "CAMERA": "camera",
    "NEURAL": "neural",
    "DATABASE": "database",
    "API": "api",
    "WEBSOCKET": "websocket",
    "SYSTEM": "system"
}

# Цвета для консольного вывода (если поддерживается)
LOG_COLORS = {
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",      # Red
    "CRITICAL": "\033[35m",   # Magenta
    "RESET": "\033[0m"        # Reset
}
