# Drone Management System

Этот проект предоставляет веб-интерфейс для управления дронами в реальном времени. Вы можете запускать и приземлять дроны через веб-страницу, а также получать информацию о погоде в выбранном городе.

## Особенности

- Управление дронами в реальном времени через веб-интерфейс.
- Проверка погоды в выбранном городе через OpenWeatherMap API.
- Логирование действий дронов и мониторинг уровня заряда батареи.

## Структура проекта

- **client.html**: Фронтенд для управления дроном, включает:
  - Выбор доступного дрона.
  - Кнопки для взлета и посадки дронов.
  - Лог для отображения информации в реальном времени.
  - Ввод для получения информации о погоде в городе.
  
- **server.py**: Сервер, обрабатывающий команды дронов через WebSocket и взаимодействующий с базой данных SQLite для хранения данных о дронах.

- **drone.py**: Логика работы дронов, включая паттерны "Декоратор" и "Пул объектов".

- **drones.db**: Файл базы данных SQLite, хранящий информацию о дронах.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/KathArdia/BPLA_project.git
   cd BPLA_project

2. Установите зависимости: Для работы с сервером и базой данных вам нужно установить зависимости:
   ```bash
   pip install websockets aiosqlite

3. Запустите сервер: Для работы с дронами и сервером выполните следующую команду:
   ```bash
   python server.py
   
4. Откройте `client.html` в браузере для управления дронами.

## Использование

1. Откройте файл `client.html` в браузере.
2. Выберите доступный дрон в выпадающем списке.
3. Нажмите кнопку "Взлет" для запуска дрона.
4. Нажмите кнопку "Посадка" для возвращения дрона.
5. Для проверки погоды введите название города и нажмите кнопку "Запросить погоду".

## Лицензия

Этот проект лицензирован под MIT License.

