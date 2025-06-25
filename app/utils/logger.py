"""
Настройка логирования
"""
import logging
import sys
from datetime import datetime


def setup_logger(name: str = "camera_monitoring", level: int = logging.INFO) -> logging.Logger:
    """Настройка логгера"""
    
    # Создание логгера
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Проверка, что обработчики еще не добавлены
    if not logger.handlers:
        # Создание форматтера
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Файловый обработчик
        file_handler = logging.FileHandler(
            f"logs/camera_monitoring_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Создание директории для логов
import os
os.makedirs("logs", exist_ok=True)

# Основной логгер приложения
logger = setup_logger()
