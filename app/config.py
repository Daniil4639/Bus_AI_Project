"""
Конфигурация приложения (обновлено для интеграции с готовой нейросетью)
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Settings:
    """Настройки приложения"""
    
    def __init__(self):
        # База данных
        self.database_url: str = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/camera_monitoring"
        )
        
        # RTSP камера
        self.rtsp_url: str = os.getenv(
            "RTSP_URL", 
            "rtsp://admin:admin@192.168.1.107:554/live.sdp"
        )
        
        # Сервер
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Параметры камеры - обновлено для 25 FPS
        self.camera_width: int = int(os.getenv("CAMERA_WIDTH", "1920"))
        self.camera_height: int = int(os.getenv("CAMERA_HEIGHT", "1080"))
        self.camera_fps: int = int(os.getenv("CAMERA_FPS", "25"))
        
        # Параметры анализа (оптимизировано для анализа безопасности водителя)
        self.analysis_interval: float = float(os.getenv("ANALYSIS_INTERVAL", "2.0"))  # Увеличено до 2 сек для сложной нейросети
        self.max_detection_results: int = int(os.getenv("MAX_DETECTION_RESULTS", "50"))
        
        # Параметры сжатия видео
        self.jpeg_quality: int = int(os.getenv("JPEG_QUALITY", "80"))
        
        # Параметры логирования
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("LOG_FILE", "logs/camera_monitoring.log")
        
        # Параметры безопасности
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        
        # Параметры производительности
        self.max_connections: int = int(os.getenv("MAX_CONNECTIONS", "100"))
        self.timeout: int = int(os.getenv("TIMEOUT", "30"))
        
        # Параметры обработки кадров для 25 FPS с учетом сложной нейросети
        self.frame_skip_count: int = int(os.getenv("FRAME_SKIP_COUNT", "50"))  # Анализ каждого 50-го кадра
        self.buffer_size: int = int(os.getenv("BUFFER_SIZE", "2"))
        
        # Параметры нейронной сети
        self.neural_network_type: str = os.getenv("NEURAL_NETWORK_TYPE", "bus_driver_safety")
        self.neural_model_path: str = os.getenv("NEURAL_MODEL_PATH", "src/")
        self.enable_mock_mode: bool = os.getenv("ENABLE_MOCK_MODE", "false").lower() == "true"
        
        # Пороги для анализа безопасности
        self.min_confidence_threshold: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.7"))
        self.warning_cooldown_seconds: int = int(os.getenv("WARNING_COOLDOWN_SECONDS", "10"))
    
    def get_database_config(self) -> dict:
        """Получение конфигурации базы данных"""
        return {
            "url": self.database_url,
            "min_size": 5,
            "max_size": 20,
            "command_timeout": self.timeout
        }
    
    def get_camera_config(self) -> dict:
        """Получение конфигурации камеры"""
        return {
            "rtsp_url": self.rtsp_url,
            "width": self.camera_width,
            "height": self.camera_height,
            "fps": self.camera_fps,
            "jpeg_quality": self.jpeg_quality,
            "frame_skip_count": self.frame_skip_count,
            "buffer_size": self.buffer_size
        }
    
    def get_neural_config(self) -> dict:
        """Получение конфигурации нейронной сети"""
        return {
            "analysis_interval": self.analysis_interval,
            "max_results": self.max_detection_results,
            "model_type": self.neural_network_type,
            "model_path": self.neural_model_path,
            "mock_mode": self.enable_mock_mode,
            "min_confidence": self.min_confidence_threshold,
            "warning_cooldown": self.warning_cooldown_seconds
        }
    
    def get_analysis_rate(self) -> float:
        """Получение частоты анализа кадров в секунду"""
        return self.camera_fps * self.analysis_interval
    
    def validate_config(self) -> list:
        """Валидация конфигурации"""
        errors = []
        
        # Проверка порта
        if not (1 <= self.port <= 65535):
            errors.append("PORT должен быть от 1 до 65535")
        
        # Проверка размеров камеры
        if self.camera_width <= 0 or self.camera_height <= 0:
            errors.append("Размеры камеры должны быть положительными")
        
        # Проверка FPS
        if not (1 <= self.camera_fps <= 60):
            errors.append("FPS должен быть от 1 до 60")
        
        # Проверка качества JPEG
        if not (1 <= self.jpeg_quality <= 100):
            errors.append("JPEG_QUALITY должен быть от 1 до 100")
        
        # Проверка параметров анализа
        if self.analysis_interval <= 0:
            errors.append("ANALYSIS_INTERVAL должен быть больше 0")
        
        # Проверка порога уверенности
        if not (0.0 <= self.min_confidence_threshold <= 1.0):
            errors.append("MIN_CONFIDENCE_THRESHOLD должен быть от 0.0 до 1.0")
        
        # Рекомендации для сложной нейросети
        if self.analysis_interval < 2.0:
            errors.append("РЕКОМЕНДАЦИЯ: Для анализа безопасности водителя рекомендуется ANALYSIS_INTERVAL >= 2.0")
        
        if self.camera_fps >= 25 and self.analysis_interval < 2.0:
            errors.append("ВНИМАНИЕ: При 25 FPS и сложной нейросети рекомендуется ANALYSIS_INTERVAL >= 2.0")
        
        return errors
    
    def __str__(self) -> str:
        """Строковое представление настроек"""
        return f"Settings(host={self.host}, port={self.port}, camera_fps={self.camera_fps}, neural_type={self.neural_network_type})"
    
    def __repr__(self) -> str:
        """Детальное представление настроек"""
        return (
            f"Settings("
            f"host='{self.host}', "
            f"port={self.port}, "
            f"camera_size={self.camera_width}x{self.camera_height}, "
            f"fps={self.camera_fps}, "
            f"analysis_interval={self.analysis_interval}, "
            f"neural_type='{self.neural_network_type}', "
            f"frame_skip={self.frame_skip_count}"
            f")"
        )


# Глобальный экземпляр настроек
settings = Settings()

# Валидация настроек при импорте
config_errors = settings.validate_config()
if config_errors:
    print("⚠️  Ошибки/рекомендации конфигурации:")
    for error in config_errors:
        print(f"   - {error}")
    print("Исправьте при необходимости в файле .env")
