"""
Модели данных для базы данных
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class DetectionResult:
    """Модель результата детекции объекта"""
    object_type: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    timestamp: str
    frame_size: Optional[List[int]] = None  # [width, height]
    
    def __post_init__(self):
        """Валидация данных после инициализации"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence должен быть от 0.0 до 1.0")
        
        if len(self.bbox) != 4:
            raise ValueError("bbox должен содержать 4 координаты [x1, y1, x2, y2]")
        
        if self.frame_size and len(self.frame_size) != 2:
            raise ValueError("frame_size должен содержать [width, height]")
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "object_type": self.object_type,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "timestamp": self.timestamp,
            "frame_size": self.frame_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectionResult":
        """Создание экземпляра из словаря"""
        return cls(
            object_type=data["object_type"],
            confidence=data["confidence"],
            bbox=data["bbox"],
            timestamp=data["timestamp"],
            frame_size=data.get("frame_size")
        )


@dataclass
class NeuralNetworkResult:
    """Модель результата работы нейронной сети"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    frame_data: Dict[str, Any] = field(default_factory=dict)
    detection_results: List[DetectionResult] = field(default_factory=list)
    processing_time: float = 0.0
    created_at: Optional[datetime] = None
    
    def add_detection(self, detection: DetectionResult):
        """Добавление результата детекции"""
        self.detection_results.append(detection)
    
    def get_object_counts(self) -> Dict[str, int]:
        """Получение количества объектов по типам"""
        counts = {}
        for detection in self.detection_results:
            object_type = detection.object_type
            counts[object_type] = counts.get(object_type, 0) + 1
        return counts
    
    def get_high_confidence_detections(self, threshold: float = 0.8) -> List[DetectionResult]:
        """Получение детекций с высокой уверенностью"""
        return [d for d in self.detection_results if d.confidence >= threshold]
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "frame_data": self.frame_data,
            "detection_results": [d.to_dict() for d in self.detection_results],
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class CameraStatistics:
    """Модель статистики камеры"""
    date: datetime
    total_frames: int = 0
    analyzed_frames: int = 0
    detected_objects: int = 0
    average_processing_time: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_analysis_rate(self) -> float:
        """Расчет процента проанализированных кадров"""
        if self.total_frames == 0:
            return 0.0
        return (self.analyzed_frames / self.total_frames) * 100
    
    def calculate_detection_rate(self) -> float:
        """Расчет среднего количества объектов на кадр"""
        if self.analyzed_frames == 0:
            return 0.0
        return self.detected_objects / self.analyzed_frames
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "date": self.date.isoformat() if self.date else None,
            "total_frames": self.total_frames,
            "analyzed_frames": self.analyzed_frames,
            "detected_objects": self.detected_objects,
            "average_processing_time": self.average_processing_time,
            "analysis_rate": self.calculate_analysis_rate(),
            "detection_rate": self.calculate_detection_rate(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class DatabaseResponse:
    """Модель ответа базы данных"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None
    count: Optional[int] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        """Автоматический расчет количества записей"""
        if self.data and self.count is None:
            self.count = len(self.data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        result = {
            "success": self.success,
            "count": self.count
        }
        
        if self.data is not None:
            result["data"] = self.data
        
        if self.message:
            result["message"] = self.message
            
        if self.error:
            result["error"] = self.error
            
        return result
    
    @classmethod
    def success_response(cls, data: List[Dict[str, Any]], message: str = None) -> "DatabaseResponse":
        """Создание успешного ответа"""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(cls, error: str, message: str = None) -> "DatabaseResponse":
        """Создание ответа с ошибкой"""
        return cls(success=False, error=error, message=message)


# Константы для моделей
DETECTION_CONFIDENCE_THRESHOLDS = {
    "LOW": 0.5,
    "MEDIUM": 0.7,
    "HIGH": 0.9
}

OBJECT_TYPES = [
    "person", "car", "bicycle", "motorcycle", "bus", "truck",
    "traffic_light", "stop_sign", "dog", "cat", "bird",
    "bottle", "chair", "couch", "plant", "bed", "table"
]

# Валидаторы
def validate_bbox(bbox: List[int]) -> bool:
    """Валидация координат ограничивающего прямоугольника"""
    if len(bbox) != 4:
        return False
    
    x1, y1, x2, y2 = bbox
    return x1 < x2 and y1 < y2 and all(coord >= 0 for coord in bbox)


def validate_confidence(confidence: float) -> bool:
    """Валидация уверенности детекции"""
    return 0.0 <= confidence <= 1.0


def validate_object_type(object_type: str) -> bool:
    """Валидация типа объекта"""
    return object_type.lower() in [obj.lower() for obj in OBJECT_TYPES]
