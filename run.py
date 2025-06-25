#!/usr/bin/env python3
"""
Точка входа для запуска системы мониторинга IP камер (оптимизировано для 25 FPS)
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

try:
    import uvicorn
    from app.main import app
    from app.config import settings
    from app.utils.logger import logger
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
    sys.exit(1)


def check_environment():
    """Проверка окружения перед запуском"""
    logger.info("Проверка окружения для работы с 25 FPS...")
    
    # Проверка директорий
    required_dirs = ['static/css', 'static/js', 'templates', 'logs']
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Проверка файла конфигурации
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("Файл .env не найден, будут использованы настройки по умолчанию")
        
        # Создание примера .env файла с настройками для 25 FPS
        example_env = """# Настройки базы данных
DATABASE_URL=postgresql://postgres:password@localhost:5432/camera_monitoring

# Настройки RTSP камеры (25 FPS)
RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream

# Настройки сервера
HOST=0.0.0.0
PORT=8000

# Параметры камеры - настроено для 25 FPS
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
CAMERA_FPS=25

# Параметры анализа (рекомендуется для 25 FPS)
ANALYSIS_INTERVAL=1.0
MAX_DETECTION_RESULTS=50

# Параметры сжатия видео
JPEG_QUALITY=80

# Параметры обработки для 25 FPS
FRAME_SKIP_COUNT=25
BUFFER_SIZE=2

# Параметры логирования
LOG_LEVEL=INFO
LOG_FILE=logs/camera_monitoring.log
"""
        
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(example_env)
        
        logger.info("Создан файл .env.example с примером конфигурации для 25 FPS")
    
    # Проверка настроек для 25 FPS
    if settings.camera_fps != 25:
        logger.warning(f"Камера настроена на {settings.camera_fps} FPS, рекомендуется 25 FPS")
    
    if settings.analysis_interval < 1.0:
        logger.warning(f"Интервал анализа {settings.analysis_interval}с может быть слишком частым для 25 FPS")
    
    logger.info("Проверка окружения завершена")


def print_system_info():
    """Вывод информации о системе"""
    print("🎥 Система мониторинга IP камер (25 FPS)")
    print("=" * 60)
    print(f"📅 Дата запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Пользователь: RiddlerXenon")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print("=" * 60)


def print_configuration():
    """Вывод конфигурации системы"""
    config = settings.get_camera_config()
    neural_config = settings.get_neural_config()
    
    print("\n⚙️  Конфигурация системы:")
    print(f"🌐 Сервер: {settings.host}:{settings.port}")
    print(f"📹 RTSP: {settings.rtsp_url}")
    print(f"🗃️  База данных: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'локальная'}")
    print(f"📏 Разрешение: {config['width']}x{config['height']}")
    print(f"🎬 FPS: {config['fps']}")
    print(f"🔍 Анализ: каждые {neural_config['analysis_interval']}с")
    print(f"📊 Буфер: {config['buffer_size']} кадра")
    print(f"🗜️  Качество JPEG: {config['jpeg_quality']}%")


def print_performance_tips():
    """Вывод советов по производительности для 25 FPS"""
    print("\n💡 Советы по оптимизации для 25 FPS:")
    print("• Убедитесь, что система имеет достаточную производительность")
    print("• Рекомендуется минимум 4 ГБ RAM и 2-ядерный процессор")
    print("• Стабильное сетевое соединение критично для RTSP потока")
    print("• Мониторьте эффективность анализа через веб-интерфейс")
    print("• При низкой производительности увеличьте ANALYSIS_INTERVAL")
    print("• Используйте SSD для базы данных при высокой нагрузке")


def main():
    """Основная функция запуска приложения"""
    try:
        print_system_info()
        
        # Проверка окружения
        check_environment()
        
        # Вывод конфигурации
        print_configuration()
        
        # Советы по производительности
        print_performance_tips()
        
        print(f"\n🚀 Запуск сервера...")
        print("Для остановки нажмите Ctrl+C")
        print("=" * 60)
        
        # Запуск сервера с оптимизацией для 25 FPS
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=True,
            log_level="info",
            access_log=True,
            reload_dirs=["app", "static", "templates"],
            # Дополнительные настройки для высокой нагрузки
            workers=1,  # Один воркер для лучшей производительности при 25 FPS
            loop="asyncio",  # Указание event loop
            http="httptools",  # Быстрый HTTP парсер
            lifespan="on"  # Включение lifespan events
        )
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки от пользователя")
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        print(f"\n❌ Ошибка запуска: {e}")
        print("Проверьте логи для получения подробной информации")
        print("Файл логов: logs/camera_monitoring.log")
        sys.exit(1)
    finally:
        print(f"\n📊 Статистика сеанса:")
        print(f"⏱️  Время работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Спасибо за использование системы мониторинга IP камер!")


if __name__ == "__main__":
    main()
