"""
Сервис для работы с IP камерой (оптимизирован для 25 FPS)
"""
import asyncio
import cv2
import numpy as np
from typing import Optional
import time
import os

from app.utils.logger import logger
from app.config import settings
from app.services.neural_service import neural_service
from app.database.connection import db_manager


class CameraService:
    """Сервис для работы с IP камерой (оптимизирован для 25 FPS)"""
    
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.last_analysis_time = 0
        self.frame_count = 0
        self.analyzed_frame_count = 0
        self.start_time = None
        self.error_count = 0
        self.max_errors = 10
        self.frame_skip_counter = 0  # Счетчик для пропуска кадров
        
    async def start_streaming(self) -> bool:
        """Запуск обработки потока с камеры (оптимизирован для 25 FPS)"""
        if self.running:
            logger.warning("Камера уже запущена")
            return False
        
        try:
            # Подключение к камере
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # Настройка параметров камеры для 25 FPS
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.camera_height)
            self.cap.set(cv2.CAP_PROP_FPS, settings.camera_fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, settings.buffer_size)
            
            # Дополнительные настройки для RTSP и 25 FPS
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
            
            # Настройки для уменьшения задержки при высоком FPS
            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (
                'rtsp_transport;udp|'
                'fflags;nobuffer|'
                'flags;low_delay|'
                'framedrop;1'
            )
            
            if not self.cap.isOpened():
                logger.error("Не удалось подключиться к камере")
                return False
            
            # Тестовое чтение кадра
            ret, test_frame = self.cap.read()
            if not ret:
                logger.error("Не удалось получить тестовый кадр с камеры")
                return False
            
            # Получение фактических параметров камеры
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.running = True
            self.frame_count = 0
            self.analyzed_frame_count = 0
            self.error_count = 0
            self.frame_skip_counter = 0
            self.start_time = time.time()
            self.last_analysis_time = time.time()
            
            logger.info(f"Камера подключена: {self.rtsp_url}")
            logger.info(f"Параметры: {actual_width}x{actual_height} @ {actual_fps} FPS")
            logger.info(f"Анализ: каждые {settings.analysis_interval} сек (примерно каждый {int(actual_fps * settings.analysis_interval)} кадр)")
            
            # Запуск асинхронной обработки кадров
            asyncio.create_task(self._process_frames())
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при запуске камеры: {e}")
            await self.stop_streaming()
            return False
    
    async def stop_streaming(self) -> None:
        """Остановка обработки потока"""
        self.running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Камера остановлена")
    
    async def _process_frames(self) -> None:
        """Основной цикл обработки кадров (оптимизирован для 25 FPS)"""
        consecutive_errors = 0
        last_fps_log = time.time()
        
        # Расчет интервала для анализа кадров
        frames_per_analysis = int(settings.camera_fps * settings.analysis_interval)
        
        logger.info(f"Запуск обработки: анализ каждого {frames_per_analysis}-го кадра")
        
        while self.running:
            loop_start = time.time()
            
            try:
                # Получение кадра
                ret, frame = self.cap.read()
                
                if not ret:
                    consecutive_errors += 1
                    logger.warning(f"Не удалось получить кадр с камеры (ошибка {consecutive_errors})")
                    
                    if consecutive_errors >= 5:
                        logger.error("Слишком много ошибок чтения кадров, останавливаем поток")
                        break
                    
                    await asyncio.sleep(0.1)
                    continue
                
                # Сброс счетчика ошибок при успешном чтении
                consecutive_errors = 0
                self.frame_count += 1
                current_time = time.time()
                
                # Анализ кадра по таймеру (каждую секунду)
                if current_time - self.last_analysis_time >= settings.analysis_interval:
                    self.last_analysis_time = current_time
                    self.analyzed_frame_count += 1
                    asyncio.create_task(self._analyze_frame(frame.copy()))
                
                # Логирование FPS каждые 30 секунд
                if current_time - last_fps_log >= 30:
                    uptime = current_time - self.start_time
                    current_fps = self.frame_count / uptime if uptime > 0 else 0
                    analysis_rate = self.analyzed_frame_count / uptime if uptime > 0 else 0
                    
                    logger.info(f"Статистика: {current_fps:.1f} FPS получено, {analysis_rate:.2f} анализов/сек")
                    last_fps_log = current_time
                
                # Адаптивная задержка для снижения нагрузки CPU
                # Не пытаемся поддерживать точный FPS, просто уменьшаем нагрузку
                processing_time = time.time() - loop_start
                if processing_time < 0.02:  # Если обработка заняла меньше 20мс
                    await asyncio.sleep(0.01)  # Небольшая пауза
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"Ошибка в цикле обработки кадров: {e}")
                
                if self.error_count >= self.max_errors:
                    logger.error("Превышен лимит ошибок, останавливаем камеру")
                    break
                
                await asyncio.sleep(1.0)
        
        # Остановка при выходе из цикла
        await self.stop_streaming()
    
    async def _analyze_frame(self, frame: np.ndarray) -> None:
        """Асинхронный анализ кадра нейронной сетью"""
        try:
            analysis_start = time.time()
            
            # Обработка кадра нейронной сетью
            results, processing_time = await neural_service.process_frame(frame)
            
            # Сохранение результатов в базу данных
            await db_manager.save_neural_result(results, processing_time)
            
            total_time = time.time() - analysis_start
            logger.debug(f"Анализ кадра завершен за {total_time:.3f}с (нейросеть: {processing_time:.3f}с)")
                
        except Exception as e:
            logger.error(f"Ошибка при анализе кадра: {e}")
    
    def get_status(self) -> dict:
        """Получение статуса камеры"""
        uptime = time.time() - self.start_time if self.start_time else 0
        fps = self.frame_count / uptime if uptime > 0 else 0
        analysis_rate = self.analyzed_frame_count / uptime if uptime > 0 else 0
        
        return {
            "active": self.running,
            "frame_count": self.frame_count,
            "analyzed_frame_count": self.analyzed_frame_count,
            "uptime": uptime,
            "current_fps": round(fps, 2),
            "analysis_rate": round(analysis_rate, 3),
            "target_fps": settings.camera_fps,
            "analysis_interval": settings.analysis_interval,
            "rtsp_url": self.rtsp_url,
            "error_count": self.error_count,
            "last_analysis": self.last_analysis_time,
            "analysis_only": True,
            "efficiency": round((analysis_rate / (1/settings.analysis_interval)) * 100, 1) if settings.analysis_interval > 0 else 0
        }
    
    def is_running(self) -> bool:
        """Проверка, запущена ли камера"""
        return self.running
    
    async def restart_camera(self) -> bool:
        """Перезапуск камеры"""
        logger.info("Перезапуск камеры...")
        await self.stop_streaming()
        await asyncio.sleep(3)  # Увеличенная пауза для стабильности
        return await self.start_streaming()
    
    def get_camera_info(self) -> dict:
        """Получение информации о камере"""
        if not self.cap or not self.cap.isOpened():
            return {"connected": False}
        
        try:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
            buffer_size = int(self.cap.get(cv2.CAP_PROP_BUFFERSIZE))
            
            # Декодирование FOURCC
            fourcc_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            return {
                "connected": True,
                "width": width,
                "height": height,
                "fps": fps,
                "target_fps": settings.camera_fps,
                "codec": fourcc_str,
                "buffer_size": buffer_size,
                "analysis_only": True,
                "optimized_for_25fps": True
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о камере: {e}")
            return {"connected": False, "error": str(e)}
    
    def get_performance_stats(self) -> dict:
        """Получение статистики производительности"""
        if not self.start_time:
            return {}
        
        uptime = time.time() - self.start_time
        fps = self.frame_count / uptime if uptime > 0 else 0
        analysis_rate = self.analyzed_frame_count / uptime if uptime > 0 else 0
        expected_analysis_rate = 1 / settings.analysis_interval if settings.analysis_interval > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "total_frames": self.frame_count,
            "analyzed_frames": self.analyzed_frame_count,
            "average_fps": round(fps, 2),
            "analysis_rate_per_second": round(analysis_rate, 3),
            "expected_analysis_rate": round(expected_analysis_rate, 3),
            "analysis_efficiency_percent": round((analysis_rate / expected_analysis_rate) * 100, 1) if expected_analysis_rate > 0 else 0,
            "frames_per_analysis": round(fps / analysis_rate, 1) if analysis_rate > 0 else 0,
            "error_count": self.error_count,
            "error_rate_percent": round((self.error_count / self.frame_count) * 100, 2) if self.frame_count > 0 else 0
        }


# Глобальный экземпляр сервиса камеры
camera_service = CameraService(settings.rtsp_url)
