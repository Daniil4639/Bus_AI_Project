"""
Утилиты для сервисов
"""
import asyncio
from typing import Any, Callable, Optional
from datetime import datetime
import functools

from app.utils.logger import logger


def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Декоратор для повторных попыток выполнения асинхронных функций
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(f"Попытка {attempt + 1}/{max_attempts} не удалась для {func.__name__}: {e}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"Все попытки исчерпаны для {func.__name__}: {e}")
            
            raise last_exception
        
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Функция {func.__name__} выполнена за {execution_time:.3f} сек")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Функция {func.__name__} завершилась с ошибкой за {execution_time:.3f} сек: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Функция {func.__name__} выполнена за {execution_time:.3f} сек")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Функция {func.__name__} завершилась с ошибкой за {execution_time:.3f} сек: {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class AsyncContextManager:
    """Базовый класс для асинхронных контекстных менеджеров"""
    
    async def __aenter__(self):
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def setup(self):
        """Настройка ресурсов"""
        pass
    
    async def cleanup(self):
        """Очистка ресурсов"""
        pass


def format_bytes(bytes_count: int) -> str:
    """Форматирование размера в байтах"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} ПБ"


def format_duration(seconds: float) -> str:
    """Форматирование продолжительности в удобочитаемый вид"""
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} мин"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} ч"
