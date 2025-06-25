"""
HTTP маршруты API (обновлено для 25 FPS)
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any

from app.services.camera_service import camera_service
from app.services.neural_service import neural_service
from app.database.connection import db_manager
from app.utils.logger import logger
from app.config import settings

# Создание роутера
router = APIRouter()

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Главная страница приложения"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api/camera/status")
async def get_camera_status() -> Dict[str, Any]:
    """Получение статуса камеры (расширенная информация для 25 FPS)"""
    try:
        camera_status = camera_service.get_status()
        camera_info = camera_service.get_camera_info()
        neural_stats = neural_service.get_processing_statistics()
        performance_stats = camera_service.get_performance_stats()
        
        return {
            "success": True,
            "camera": {
                **camera_status,
                "info": camera_info,
                "performance": performance_stats
            },
            "neural_network": neural_stats,
            "config": {
                "target_fps": settings.camera_fps,
                "analysis_interval": settings.analysis_interval,
                "expected_analysis_rate": round(1 / settings.analysis_interval, 3) if settings.analysis_interval > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса камеры: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статуса")


@router.post("/api/camera/start")
async def start_camera() -> Dict[str, Any]:
    """Запуск камеры"""
    try:
        if camera_service.is_running():
            return {
                "success": False,
                "message": "Камера уже запущена"
            }
        
        success = await camera_service.start_streaming()
        
        if success:
            return {
                "success": True,
                "message": f"Камера запущена (25 FPS, анализ каждые {settings.analysis_interval}с)"
            }
        else:
            return {
                "success": False,
                "message": "Не удалось запустить камеру. Проверьте RTSP URL и настройки сети."
            }
            
    except Exception as e:
        logger.error(f"Ошибка запуска камеры: {e}")
        raise HTTPException(status_code=500, detail="Ошибка запуска камеры")


@router.post("/api/camera/stop")
async def stop_camera() -> Dict[str, Any]:
    """Остановка камеры"""
    try:
        await camera_service.stop_streaming()
        return {
            "success": True,
            "message": "Камера остановлена"
        }
    except Exception as e:
        logger.error(f"Ошибка остановки камеры: {e}")
        raise HTTPException(status_code=500, detail="Ошибка остановки камеры")


@router.post("/api/camera/restart")
async def restart_camera() -> Dict[str, Any]:
    """Перезапуск камеры"""
    try:
        success = await camera_service.restart_camera()
        
        if success:
            return {
                "success": True,
                "message": "Камера успешно перезапущена"
            }
        else:
            return {
                "success": False,
                "message": "Не удалось перезапустить камеру"
            }
    except Exception as e:
        logger.error(f"Ошибка перезапуска камеры: {e}")
        raise HTTPException(status_code=500, detail="Ошибка перезапуска камеры")


@router.get("/api/camera/performance")
async def get_camera_performance() -> Dict[str, Any]:
    """Получение детальной статистики производительности"""
    try:
        performance_stats = camera_service.get_performance_stats()
        
        return {
            "success": True,
            "data": performance_stats,
            "recommendations": _get_performance_recommendations(performance_stats)
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики производительности: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


def _get_performance_recommendations(stats: Dict[str, Any]) -> list:
    """Генерация рекомендаций по оптимизации производительности"""
    recommendations = []
    
    if not stats:
        return recommendations
    
    # Проверка эффективности анализа
    efficiency = stats.get("analysis_efficiency_percent", 0)
    if efficiency < 90:
        recommendations.append(
            f"Эффективность анализа {efficiency}% - рассмотрите увеличение ANALYSIS_INTERVAL"
        )
    
    # Проверка FPS
    avg_fps = stats.get("average_fps", 0)
    if avg_fps < 20:
        recommendations.append(
            f"Низкий FPS ({avg_fps}) - проверьте сетевое соединение и производительность системы"
        )
    
    # Проверка ошибок
    error_rate = stats.get("error_rate_percent", 0)
    if error_rate > 5:
        recommendations.append(
            f"Высокий процент ошибок ({error_rate}%) - проверьте стабильность RTSP потока"
        )
    
    # Проверка соотношения кадров к анализу
    frames_per_analysis = stats.get("frames_per_analysis", 0)
    if frames_per_analysis > 30:
        recommendations.append(
            f"Много кадров между анализами ({frames_per_analysis}) - можно уменьшить ANALYSIS_INTERVAL"
        )
    
    return recommendations


@router.get("/api/database/results")
async def get_database_results(limit: int = 50) -> Dict[str, Any]:
    """Получение результатов из базы данных"""
    try:
        # Ограничиваем максимальное количество результатов
        limit = min(limit, 1000)
        
        results = await db_manager.get_recent_results(limit)
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Ошибка получения данных из базы: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения данных из базы данных")


@router.get("/api/database/statistics")
async def get_database_statistics(days: int = 7) -> Dict[str, Any]:
    """Получение статистики из базы данных"""
    try:
        # Ограничиваем период
        days = min(days, 365)
        
        stats = await db_manager.get_statistics(days)
        return {
            "success": True,
            "data": stats,
            "count": len(stats)
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.get("/api/database/info")
async def get_database_info() -> Dict[str, Any]:
    """Получение информации о базе данных"""
    try:
        info = await db_manager.get_database_info()
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о базе данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения информации о базе данных")


@router.post("/api/database/cleanup")
async def cleanup_database(days_to_keep: int = 30) -> Dict[str, Any]:
    """Очистка старых данных из базы"""
    try:
        # Минимум 7 дней, максимум 365
        days_to_keep = max(7, min(days_to_keep, 365))
        
        deleted_count = await db_manager.cleanup_old_data(days_to_keep)
        return {
            "success": True,
            "message": f"Удалено {deleted_count} записей старше {days_to_keep} дней",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"Ошибка очистки базы данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка очистки данных")


@router.get("/api/neural/statistics")
async def get_neural_statistics() -> Dict[str, Any]:
    """Получение статистики нейронной сети"""
    try:
        stats = neural_service.get_processing_statistics()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики нейронной сети: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")


@router.post("/api/neural/reset-statistics")
async def reset_neural_statistics() -> Dict[str, Any]:
    """Сброс статистики нейронной сети"""
    try:
        neural_service.reset_statistics()
        return {
            "success": True,
            "message": "Статистика сброшена"
        }
    except Exception as e:
        logger.error(f"Ошибка сброса статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сброса статистики")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Проверка здоровья приложения"""
    try:
        # Проверка состояния компонентов
        camera_running = camera_service.is_running()
        neural_loaded = neural_service.model_loaded
        database_connected = db_manager.pool is not None
        
        # Дополнительная проверка базы данных
        db_info = await db_manager.get_database_info()
        database_healthy = bool(db_info)
        
        # Получение статистики производительности
        performance_stats = camera_service.get_performance_stats() if camera_running else {}
        
        # Общее состояние
        overall_status = "healthy" if all([
            database_connected,
            database_healthy,
            neural_loaded
        ]) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "config": {
                "target_fps": settings.camera_fps,
                "analysis_interval": settings.analysis_interval,
                "optimized_for_25fps": True
            },
            "components": {
                "camera": {
                    "running": camera_running,
                    "status": "healthy" if camera_running else "stopped",
                    "mode": "analysis_only_25fps",
                    "performance": performance_stats
                },
                "neural_network": {
                    "loaded": neural_loaded,
                    "status": "healthy" if neural_loaded else "loading"
                },
                "database": {
                    "connected": database_connected,
                    "healthy": database_healthy,
                    "status": "healthy" if database_healthy else "error"
                }
            },
            "database_info": db_info if database_healthy else None
        }
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {
            "status": "error",
            "error": str(e),
            "components": {
                "camera": {"status": "unknown"},
                "neural_network": {"status": "unknown"},  
                "database": {"status": "error"}
            }
        }
