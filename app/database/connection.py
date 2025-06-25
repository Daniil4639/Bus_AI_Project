"""
Управление соединениями с базой данных
"""
import asyncpg
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from app.config import settings
from app.utils.logger import logger


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self) -> None:
        """Создание пула соединений с базой данных"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            await self.create_tables()
            logger.info("Подключение к базе данных успешно установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    async def create_tables(self) -> None:
        """Создание таблиц в базе данных"""
        try:
            async with self.pool.acquire() as conn:
                # Создание основной таблицы для результатов
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS neural_network_results (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        frame_data JSONB NOT NULL DEFAULT '{}',
                        detection_results JSONB NOT NULL DEFAULT '[]',
                        processing_time REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Создание индексов для оптимизации
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_neural_results_timestamp 
                    ON neural_network_results(timestamp DESC)
                ''')
                
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_neural_results_created_at 
                    ON neural_network_results(created_at DESC)
                ''')
                
                # Создание таблицы для статистики с правильным UNIQUE constraint
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS camera_statistics (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        total_frames INTEGER DEFAULT 0,
                        analyzed_frames INTEGER DEFAULT 0,
                        detected_objects INTEGER DEFAULT 0,
                        average_processing_time REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date)
                    )
                ''')
                
                # Создание индекса для таблицы статистики
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_camera_statistics_date 
                    ON camera_statistics(date DESC)
                ''')
                
                logger.info("Таблицы базы данных созданы успешно")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            raise
    
    async def save_neural_result(
        self, 
        detection_results: List[Dict[str, Any]], 
        processing_time: float = 0.0
    ) -> int:
        """Сохранение результатов работы нейронной сети"""
        try:
            async with self.pool.acquire() as conn:
                # Сохранение результата
                result = await conn.fetchrow('''
                    INSERT INTO neural_network_results 
                    (frame_data, detection_results, processing_time)
                    VALUES ($1, $2, $3)
                    RETURNING id
                ''', 
                json.dumps({"frame_processed": True, "timestamp": datetime.now().isoformat()}),
                json.dumps(detection_results),
                processing_time
                )
                
                # Обновление статистики
                await self.update_daily_statistics(len(detection_results), processing_time)
                
                logger.info(f"Результаты нейронной сети сохранены с ID: {result['id']}")
                return result['id']
                
        except Exception as e:
            logger.error(f"Ошибка сохранения в базу данных: {e}")
            raise
    
    async def get_recent_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение последних результатов из базы данных"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT 
                        id, 
                        timestamp, 
                        frame_data, 
                        detection_results, 
                        processing_time,
                        created_at
                    FROM neural_network_results
                    ORDER BY timestamp DESC
                    LIMIT $1
                ''', limit)
                
                # Преобразование результатов
                results = []
                for row in rows:
                    results.append({
                        'id': row['id'],
                        'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None,
                        'frame_data': row['frame_data'],
                        'detection_results': row['detection_results'],
                        'processing_time': row['processing_time'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None
                    })
                
                logger.debug(f"Получено {len(results)} записей из базы данных")
                return results
                
        except Exception as e:
            logger.error(f"Ошибка получения данных из базы: {e}")
            return []
    
    async def update_daily_statistics(self, detected_objects_count: int, processing_time: float = 0.0) -> None:
        """Обновление ежедневной статистики"""
        try:
            current_date = date.today()
            
            async with self.pool.acquire() as conn:
                # Проверяем, существует ли запись для текущей даты
                existing_record = await conn.fetchrow('''
                    SELECT id, analyzed_frames, detected_objects, average_processing_time
                    FROM camera_statistics 
                    WHERE date = $1
                ''', current_date)
                
                if existing_record:
                    # Обновляем существующую запись
                    old_analyzed_frames = existing_record['analyzed_frames']
                    old_detected_objects = existing_record['detected_objects']
                    old_avg_time = existing_record['average_processing_time']
                    
                    # Расчет нового среднего времени обработки
                    new_analyzed_frames = old_analyzed_frames + 1
                    new_detected_objects = old_detected_objects + detected_objects_count
                    
                    if old_analyzed_frames > 0:
                        new_avg_time = ((old_avg_time * old_analyzed_frames) + processing_time) / new_analyzed_frames
                    else:
                        new_avg_time = processing_time
                    
                    await conn.execute('''
                        UPDATE camera_statistics 
                        SET analyzed_frames = $1,
                            detected_objects = $2,
                            average_processing_time = $3,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE date = $4
                    ''', new_analyzed_frames, new_detected_objects, new_avg_time, current_date)
                    
                    logger.debug(f"Обновлена статистика для {current_date}: кадров={new_analyzed_frames}, объектов={new_detected_objects}")
                else:
                    # Создаем новую запись
                    await conn.execute('''
                        INSERT INTO camera_statistics 
                        (date, analyzed_frames, detected_objects, average_processing_time)
                        VALUES ($1, 1, $2, $3)
                    ''', current_date, detected_objects_count, processing_time)
                    
                    logger.debug(f"Создана новая статистика для {current_date}: объектов={detected_objects_count}")
                
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    async def get_statistics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Получение статистики за последние дни"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT 
                        date,
                        total_frames,
                        analyzed_frames,
                        detected_objects,
                        average_processing_time,
                        created_at,
                        updated_at
                    FROM camera_statistics
                    WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                    ORDER BY date DESC
                ''' % days)
                
                results = []
                for row in rows:
                    results.append({
                        'date': row['date'].isoformat() if row['date'] else None,
                        'total_frames': row['total_frames'],
                        'analyzed_frames': row['analyzed_frames'],
                        'detected_objects': row['detected_objects'],
                        'average_processing_time': row['average_processing_time'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return []
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Очистка старых данных"""
        try:
            async with self.pool.acquire() as conn:
                # Очистка старых результатов анализа
                result = await conn.fetchrow('''
                    WITH deleted AS (
                        DELETE FROM neural_network_results
                        WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
                        RETURNING id
                    )
                    SELECT COUNT(*) as deleted_count FROM deleted
                ''' % days_to_keep)
                
                deleted_count = result['deleted_count'] if result else 0
                
                # Очистка старой статистики (оставляем больше данных для статистики)
                stats_days = max(days_to_keep * 2, 90)  # Минимум 90 дней статистики
                await conn.execute('''
                    DELETE FROM camera_statistics
                    WHERE date < CURRENT_DATE - INTERVAL '%s days'
                ''' % stats_days)
                
                if deleted_count > 0:
                    logger.info(f"Удалено {deleted_count} старых записей")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Ошибка очистки данных: {e}")
            return 0
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Получение информации о базе данных"""
        try:
            async with self.pool.acquire() as conn:
                # Общая информация
                db_size = await conn.fetchrow('''
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size
                ''')
                
                # Количество записей в таблицах
                results_count = await conn.fetchval('''
                    SELECT COUNT(*) FROM neural_network_results
                ''')
                
                stats_count = await conn.fetchval('''
                    SELECT COUNT(*) FROM camera_statistics
                ''')
                
                # Последняя активность
                last_result = await conn.fetchrow('''
                    SELECT created_at FROM neural_network_results 
                    ORDER BY created_at DESC LIMIT 1
                ''')
                
                return {
                    'database_size': db_size['size'] if db_size else 'Unknown',
                    'results_count': results_count,
                    'statistics_count': stats_count,
                    'last_activity': last_result['created_at'].isoformat() if last_result and last_result['created_at'] else None,
                    'pool_size': len(self.pool._holders) if self.pool else 0,
                    'pool_max_size': self.pool._maxsize if self.pool else 0
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о базе данных: {e}")
            return {}
    
    async def close_pool(self) -> None:
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Пул соединений с базой данных закрыт")


# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager(settings.database_url)
