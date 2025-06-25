"""
Основное приложение FastAPI (без WebSocket)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import db_manager
from app.services.neural_service import neural_service
from app.api.routes import router
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Запуск приложения...")
    
    try:
        # Инициализация базы данных
        await db_manager.create_pool()
        
        # Инициализация нейронной сети
        await neural_service.initialize_model()
        
        logger.info("Приложение успешно запущено (режим анализа)")
        
        yield
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        raise
    finally:
        # Завершение работы
        logger.info("Завершение работы приложения...")
        
        # Закрытие соединений
        await db_manager.close_pool()
        
        logger.info("Приложение завершено")


def create_app() -> FastAPI:
    """Создание экземпляра FastAPI приложения"""
    
    app = FastAPI(
        title="Система мониторинга IP камер (Анализ)",
        description="Веб-приложение для анализа IP камер нейронными сетями без веб-потока",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключение статических файлов
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Подключение маршрутов
    app.include_router(router)
    
    return app


# Создание приложения
app = create_app()
