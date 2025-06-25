"""
Пакет для работы с базой данных

Содержит модули для:
- Управления соединениями с PostgreSQL
- Определения моделей данных
- Миграций схемы базы данных

Основные компоненты:
- DatabaseManager: Менеджер пула соединений
- Models: Модели данных для результатов анализа
- Connection: Утилиты для работы с соединениями

Использование:
    from app.database import db_manager
    
    # Инициализация
    await db_manager.create_pool()
    
    # Сохранение результатов
    await db_manager.save_neural_result(results)
    
    # Получение данных
    data = await db_manager.get_recent_results()
"""

from app.database.connection import DatabaseManager, db_manager
from app.database.models import (
    DetectionResult,
    NeuralNetworkResult,
    CameraStatistics,
    DatabaseResponse
)

# Экспорт основных компонентов
__all__ = [
    # Менеджер базы данных
    "DatabaseManager",
    "db_manager",
    
    # Модели данных
    "DetectionResult",
    "NeuralNetworkResult", 
    "CameraStatistics",
    "DatabaseResponse",
]

# Информация о пакете
__version__ = "1.0.0"
__description__ = "Модуль для работы с базой данных PostgreSQL"

# Константы для работы с БД
DATABASE_TABLES = [
    "neural_network_results",
    "camera_statistics"
]

DATABASE_INDEXES = [
    "idx_neural_results_timestamp",
    "idx_neural_results_created_at"
]

# Настройки по умолчанию
DEFAULT_POOL_SIZE = {
    "min_size": 5,
    "max_size": 20,
    "command_timeout": 60
}

DEFAULT_CLEANUP_DAYS = 30
DEFAULT_RESULTS_LIMIT = 50
