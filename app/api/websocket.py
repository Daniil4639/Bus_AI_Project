"""
WebSocket обработчики
"""
from fastapi import WebSocket, WebSocketDisconnect
from app.services.camera_service import camera_service
from app.utils.logger import logger


async def websocket_camera_handler(websocket: WebSocket) -> None:
    """Обработчик WebSocket для потоковой передачи видео"""
    await websocket.accept()
    
    # Добавление WebSocket в сервис камеры
    camera_service.add_websocket(websocket)
    
    try:
        # Запуск камеры если она не активна
        if not camera_service.is_running():
            await camera_service.start_streaming()
        
        # Ожидание сообщений от клиента
        while True:
            try:
                # Получение сообщения (для поддержания соединения)
                message = await websocket.receive_text()
                logger.debug(f"Получено WebSocket сообщение: {message}")
                
                # Обработка команд от клиента
                if message == "ping":
                    await websocket.send_text("pong")
                elif message == "status":
                    status = camera_service.get_status()
                    await websocket.send_json(status)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Ошибка обработки WebSocket сообщения: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info("WebSocket соединение закрыто клиентом")
    except Exception as e:
        logger.error(f"Ошибка WebSocket соединения: {e}")
    finally:
        # Удаление WebSocket из сервиса камеры
        camera_service.remove_websocket(websocket)
