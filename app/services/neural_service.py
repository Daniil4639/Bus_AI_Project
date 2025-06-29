"""
Сервис для работы с нейронной сетью (интеграция с готовой моделью)
"""
import asyncio
import numpy as np
import cv2
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime
import sys
from pathlib import Path

# Добавляем путь к вашей нейросети
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.utils.logger import logger
from app.database.models import DetectionResult

# Импорт вашей нейросети
try:
    from src.main import initialize_processor, analyze_image
    from src.core.image_processor import ImageProcessor
    NEURAL_NETWORK_AVAILABLE = True
    logger.info("Нейронная сеть для анализа безопасности водителя загружена успешно")
except ImportError as e:
    NEURAL_NETWORK_AVAILABLE = False
    logger.warning(f"Не удалось загрузить нейронную сеть: {e}")
    logger.warning("Будет использован режим эмуляции")


class NeuralNetworkService:
    """Сервис для анализа кадров нейронной сетью"""
    
    def __init__(self):
        self.model_loaded = False
        self.processor = None
        self.processed_frames = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        self.last_error_time = None
        self.initialization_time = None
        
        # Статистика по типам предупреждений
        self.warning_stats = {
            "belt_not_detected": 0,
            "wheel_not_detected": 0, 
            "hands_not_on_wheel": 0,
            "objects_in_hands": 0,
            "driver_not_detected": 0,
            "total_warnings": 0
        }
        
        # Статистика по обнаруженным объектам
        self.detected_objects_stats = {
            "cell phone": 0,
            "cup": 0,
            "bottle": 0,
            "belt": 0,
            "wheel": 0,
            "person": 0
        }
    
    async def initialize_model(self) -> bool:
        """Инициализация модели нейронной сети"""
        start_time = time.time()
        
        try:
            if not NEURAL_NETWORK_AVAILABLE:
                logger.warning("Нейронная сеть недоступна, используется режим эмуляции")
                self.model_loaded = True
                self.initialization_time = time.time() - start_time
                return True
            
            logger.info("Инициализация нейронной сети для анализа безопасности водителя...")
            
            # Инициализация вашего процессора
            self.processor = initialize_processor()
            
            self.model_loaded = True
            self.initialization_time = time.time() - start_time
            
            logger.info(f"Модель нейронной сети успешно инициализирована за {self.initialization_time:.2f}с")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации модели: {e}")
            self.model_loaded = False
            return False
    
    async def process_frame(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], float]:
        """Обработка кадра нейронной сетью"""
        if not self.model_loaded:
            logger.warning("Модель не загружена")
            return [], 0.0
        
        start_time = time.time()
        
        try:
            if not NEURAL_NETWORK_AVAILABLE or self.processor is None:
                # Режим эмуляции
                return await self._generate_mock_results(frame)
            
            # Реальная обработка вашей нейросетью
            results = await self._process_with_real_network(frame)
            
            processing_time = time.time() - start_time
            self.processed_frames += 1
            self.total_processing_time += processing_time
            
            logger.debug(f"Кадр обработан за {processing_time:.3f}с, найдено {len(results)} объектов/предупреждений")
            
            return results, processing_time
            
        except Exception as e:
            self.error_count += 1
            self.last_error_time = datetime.now()
            processing_time = time.time() - start_time
            
            logger.error(f"Ошибка обработки кадра: {e}")
            return [], processing_time
    
    async def _process_with_real_network(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Обработка кадра реальной нейронной сетью"""
        results = []
        
        try:
            # Сохраняем кадр во временный файл для обработки
            # temp_image_path = "/tmp/temp_frame.jpg"
            # cv2.imwrite(temp_image_path, frame)
            
            frame_path = save_frame(frame)

            # Обработка вашей нейросетью
            warnings, image_with_boxes = analyze_image(self.processor, frame_path)
            
            current_time = datetime.now().isoformat()
            frame_height, frame_width = frame.shape[:2]
            
            # Обработка предупреждений
            for warning in warnings:
                warning_type = self._classify_warning(warning)
                self.warning_stats[warning_type] += 1
                self.warning_stats["total_warnings"] += 1
                
                # Создаем детекцию для предупреждения
                detection = {
                    "object_type": warning_type,
                    "confidence": 0.95,  # Высокая уверенность для предупреждений
                    "bbox": [0, 0, frame_width, frame_height],  # Весь кадр
                    "timestamp": current_time,
                    "frame_size": [frame_width, frame_height],
                    "warning_message": warning,
                    "detection_type": "warning"
                }
                results.append(detection)
            
            # Если нет предупреждений, добавляем положительные детекции
            if len(warnings) == 0:
                # Водитель обнаружен (если нет предупреждения о необнаружении)
                self.detected_objects_stats["person"] += 1
                results.append({
                    "object_type": "driver_detected",
                    "confidence": 0.90,
                    "bbox": [frame_width//4, frame_height//4, 3*frame_width//4, 3*frame_height//4],
                    "timestamp": current_time,
                    "frame_size": [frame_width, frame_height],
                    "detection_type": "positive"
                })
                
                # Ремень безопасности (предполагаем, что обнаружен если нет предупреждения)
                self.detected_objects_stats["belt"] += 1
                results.append({
                    "object_type": "safety_belt",
                    "confidence": 0.85,
                    "bbox": [frame_width//3, frame_height//3, 2*frame_width//3, 2*frame_height//3],
                    "timestamp": current_time,
                    "frame_size": [frame_width, frame_height],
                    "detection_type": "positive"
                })
                
                # Рулевое колесо
                self.detected_objects_stats["wheel"] += 1
                results.append({
                    "object_type": "steering_wheel",
                    "confidence": 0.88,
                    "bbox": [frame_width//3, 2*frame_height//3, 2*frame_width//3, frame_height],
                    "timestamp": current_time,
                    "frame_size": [frame_width, frame_height],
                    "detection_type": "positive"
                })
            
            # Очищаем временный файл
            # try:
            #     Path(temp_image_path).unlink()
            # except:
            #     pass
                
        except Exception as e:
            logger.error(f"Ошибка в обработке реальной нейросетью: {e}")
            # Возвращаем пустой результат при ошибке
            pass
        
        return results
    
    def _classify_warning(self, warning_message: str) -> str:
        """Классификация предупреждений по типам"""
        warning_lower = warning_message.lower()
        
        if "ремень" in warning_lower or "пристегнут" in warning_lower:
            return "belt_not_detected"
        elif "руки" in warning_lower and "руле" in warning_lower:
            return "hands_not_on_wheel"
        elif "управления" in warning_lower or "руле" in warning_lower:
            return "wheel_not_detected"
        elif "объект" in warning_lower or "руке" in warning_lower:
            return "objects_in_hands"
        elif "водитель" in warning_lower and "распознан" in warning_lower:
            return "driver_not_detected"
        else:
            return "unknown_warning"
    
    async def _generate_mock_results(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], float]:
        """Генерация тестовых результатов (режим эмуляции)"""
        import random
        
        # Имитация времени обработки
        processing_time = random.uniform(0.05, 0.15)
        await asyncio.sleep(processing_time)
        
        results = []
        current_time = datetime.now().isoformat()
        frame_height, frame_width = frame.shape[:2]
        
        # Генерация случайных результатов с правдоподобными типами для системы безопасности
        safety_scenarios = [
            # Сценарий 1: Все в порядке
            {
                "probability": 0.6,
                "detections": [
                    {"type": "driver_detected", "confidence": 0.92},
                    {"type": "safety_belt", "confidence": 0.88},
                    {"type": "steering_wheel", "confidence": 0.90}
                ]
            },
            # Сценарий 2: Не пристегнут
            {
                "probability": 0.15,
                "detections": [
                    {"type": "driver_detected", "confidence": 0.91},
                    {"type": "belt_not_detected", "confidence": 0.95},
                    {"type": "steering_wheel", "confidence": 0.89}
                ]
            },
            # Сценарий 3: Объект в руках
            {
                "probability": 0.15,
                "detections": [
                    {"type": "driver_detected", "confidence": 0.90},
                    {"type": "safety_belt", "confidence": 0.85},
                    {"type": "cell_phone", "confidence": 0.82},
                    {"type": "objects_in_hands", "confidence": 0.93}
                ]
            },
            # Сценарий 4: Руки не на руле
            {
                "probability": 0.1,
                "detections": [
                    {"type": "driver_detected", "confidence": 0.89},
                    {"type": "safety_belt", "confidence": 0.86},
                    {"type": "hands_not_on_wheel", "confidence": 0.91}
                ]
            }
        ]
        
        # Выбираем сценарий
        rand_val = random.random()
        cumulative_prob = 0
        selected_scenario = safety_scenarios[0]  # По умолчанию
        
        for scenario in safety_scenarios:
            cumulative_prob += scenario["probability"]
            if rand_val <= cumulative_prob:
                selected_scenario = scenario
                break
        
        # Генерируем детекции для выбранного сценария
        for detection_template in selected_scenario["detections"]:
            # Случайные координаты bbox
            x1 = random.randint(0, frame_width // 3)
            y1 = random.randint(0, frame_height // 3)
            x2 = random.randint(2 * frame_width // 3, frame_width)
            y2 = random.randint(2 * frame_height // 3, frame_height)
            
            detection = {
                "object_type": detection_template["type"],
                "confidence": detection_template["confidence"] + random.uniform(-0.05, 0.05),
                "bbox": [x1, y1, x2, y2],
                "timestamp": current_time,
                "frame_size": [frame_width, frame_height],
                "detection_type": "mock"
            }
            
            results.append(detection)
            
            # Обновляем статистику
            if detection_template["type"] in self.detected_objects_stats:
                self.detected_objects_stats[detection_template["type"]] += 1
            
            if "not_detected" in detection_template["type"] or "hands_not_on_wheel" in detection_template["type"] or "objects_in_hands" in detection_template["type"]:
                self.warning_stats["total_warnings"] += 1
                if detection_template["type"] in self.warning_stats:
                    self.warning_stats[detection_template["type"]] += 1
        
        self.processed_frames += 1
        self.total_processing_time += processing_time
        
        return results, processing_time
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Получение статистики обработки"""
        avg_processing_time = (
            self.total_processing_time / self.processed_frames 
            if self.processed_frames > 0 else 0.0
        )
        
        return {
            "model_loaded": self.model_loaded,
            "model_type": "bus_driver_safety_analysis" if NEURAL_NETWORK_AVAILABLE else "mock_emulation",
            "processed_frames": self.processed_frames,
            "total_processing_time": round(self.total_processing_time, 2),
            "average_processing_time": round(avg_processing_time, 3),
            "error_count": self.error_count,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "initialization_time": round(self.initialization_time, 2) if self.initialization_time else None,
            "warning_statistics": self.warning_stats.copy(),
            "detected_objects_statistics": self.detected_objects_stats.copy(),
            "efficiency": round((self.processed_frames / (self.processed_frames + self.error_count)) * 100, 1) if (self.processed_frames + self.error_count) > 0 else 100
        }
    
    def reset_statistics(self) -> None:
        """Сброс статистики"""
        self.processed_frames = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        self.last_error_time = None
        
        # Сброс статистики предупреждений
        for key in self.warning_stats:
            self.warning_stats[key] = 0
            
        # Сброс статистики объектов
        for key in self.detected_objects_stats:
            self.detected_objects_stats[key] = 0
        
        logger.info("Статистика нейронной сети сброшена")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        return {
            "model_loaded": self.model_loaded,
            "model_type": "Bus Driver Safety Analysis System",
            "capabilities": [
                "Driver pose detection",
                "Safety belt detection", 
                "Steering wheel detection",
                "Hands on wheel checking",
                "Objects in hands detection"
            ],
            "supported_objects": [
                "driver", "safety_belt", "steering_wheel", 
                "cell_phone", "cup", "bottle"
            ],
            "warning_types": [
                "belt_not_detected", "wheel_not_detected",
                "hands_not_on_wheel", "objects_in_hands", 
                "driver_not_detected"
            ],
            "framework": "MediaPipe + YOLO + OpenVINO",
            "initialization_time": self.initialization_time,
            "available": NEURAL_NETWORK_AVAILABLE
        }


# Глобальный экземпляр сервиса
neural_service = NeuralNetworkService()
