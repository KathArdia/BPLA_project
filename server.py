import asyncio
import websockets
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging
from drone import Drone, DronePool, BatteryDecorator

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Класс Фабрика для создания дронов
class DroneFactory:
    @staticmethod
    def create_drone(serial_number, model, manufacturer):
        return Drone(serial_number, model, manufacturer)

# Инициализация пула дронов
drone_pool = DronePool(5)

# Автоматическое создание 4 дронов и добавление их в базу данных
def create_default_drones():
    conn = sqlite3.connect('drones.db')
    cursor = conn.cursor()

    # Данные о дронах для добавления
    drones_data = [
        ("SN001", "ModelX", "SkyNet"),
        ("SN002", "ModelY", "SkyTech"),
        ("SN003", "ModelZ", "DroneCorp"),
        ("SN004", "ModelA", "AeroTech")
    ]

    # Добавляем дроны в базу данных и пул
    for serial_number, model, manufacturer in drones_data:
        # Используем фабрику для создания дронов
        drone = DroneFactory.create_drone(serial_number, model, manufacturer)
        cursor.execute(
            "INSERT OR IGNORE INTO drones (serial_number, model, manufacturer, battery_level) VALUES (?, ?, ?, ?)",
            (serial_number, model, manufacturer, 100))
        drone_pool._available_drones.append(drone)
        logging.info(f"Дрон {serial_number} добавлен в базу данных и пул")

    # Сохраняем изменения и закрываем подключение
    conn.commit()
    conn.close()

# Функция для получения списка дронов из базы данных
def get_drones():
    conn = sqlite3.connect('drones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT serial_number, model, manufacturer FROM drones")
    drones = cursor.fetchall()
    logging.info(f"Найдено дронов в базе данных: {len(drones)}")
    conn.close()
    return [{"serial_number": d[0], "model": d[1], "manufacturer": d[2]} for d in drones]

# Обработчик HTTP запросов для списка дронов
class DronesRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/drones":
            logging.info("Получен запрос на список дронов")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Разрешаем запросы с любого источника (CORS)
            self.end_headers()
            drones = get_drones()
            logging.info(f"Возвращаем список дронов: {drones}")
            self.wfile.write(json.dumps(drones).encode())
        else:
            logging.warning(f"Неверный путь: {self.path}")
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')  # Разрешаем запросы с любого источника (CORS)
            self.end_headers()

# Запуск HTTP сервера для обработки запросов списка дронов
def run_http_server():
    server_address = ('', 8081)
    httpd = HTTPServer(server_address, DronesRequestHandler)
    logging.info("HTTP сервер запущен на порту 8081")
    httpd.serve_forever()

# Функция для обработки WebSocket соединений
async def handle_client(websocket, path):
    logging.info("WebSocket соединение открыто")
    async for message in websocket:
        data = json.loads(message)
        logging.debug(f"Получено сообщение от клиента: {data}")
        command = data['command']

        if command == 'register':
            await websocket.send("Дроны уже зарегистрированы в системе")

        elif command == 'launch':
            serial_number = data['serial_number']
            logging.info(f"Попытка запуска дрона {serial_number}")
            drone = next(
                (d for d in drone_pool._available_drones + drone_pool._used_drones if d.serial_number == serial_number),
                None)
            if drone:
                logging.info(f"Дрон {serial_number} найден, запуск")
                decorated_drone = BatteryDecorator(drone)
                decorated_drone.launch()
                if drone in drone_pool._available_drones:
                    drone_pool._available_drones.remove(drone)
                    drone_pool._used_drones.append(drone)
                await websocket.send(f"Дрон {drone.serial_number} запущен")
            else:
                logging.error(f"Дрон {serial_number} не найден")
                await websocket.send("Дрон не найден")

        elif command == 'land':
            serial_number = data['serial_number']
            logging.info(f"Попытка посадки дрона {serial_number}")
            drone = next((d for d in drone_pool._used_drones if d.serial_number == serial_number), None)
            if drone:
                logging.info(f"Дрон {serial_number} найден, посадка")
                drone.land()
                drone_pool._used_drones.remove(drone)
                drone_pool._available_drones.append(drone)
                await websocket.send(f"Дрон {drone.serial_number} успешно приземлился")
            else:
                logging.error(f"Дрон {serial_number} не найден для посадки")
                await websocket.send("Дрон не найден для посадки")

# Запуск WebSocket сервера
async def main():
    create_default_drones()  # Создание дронов при запуске сервера
    async with websockets.serve(handle_client, "localhost", 8765):
        logging.info("WebSocket сервер запущен на ws://localhost:8765")
        await asyncio.Future()  # Ожидание завершения сервера

if __name__ == "__main__":
    # Запуск HTTP сервера в отдельном потоке
    http_thread = Thread(target=run_http_server)
    http_thread.start()

    # Запуск WebSocket сервера
    asyncio.run(main())
