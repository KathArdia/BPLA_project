import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Drone:
    def __init__(self, serial_number, model, manufacturer, battery_level=100):
        self.serial_number = serial_number
        self.model = model
        self.manufacturer = manufacturer
        self.battery_level = battery_level
        logging.info(f"Дрон {self.serial_number} создан")

    def launch(self):
        if self.battery_level > 20:
            logging.info(f"Дрон {self.serial_number} запущен")
        else:
            logging.warning(f"Низкий уровень заряда {self.battery_level}% - не могу запустить дрон")

    def land(self):
        logging.info(f"Дрон {self.serial_number} приземлился")

    def check_battery(self):
        if self.battery_level < 20:
            logging.warning(f"Уровень заряда {self.battery_level}% - вернуться на базу")
        if self.battery_level < 5:
            logging.error(f"Критический уровень заряда {self.battery_level}% - экстренная посадка")

# Паттерн "Декоратор"
class DroneDecorator:
    def __init__(self, drone: Drone):
        self._drone = drone

    def launch(self):
        print("Проверка всех систем перед запуском")
        self._drone.launch()

    def land(self):
        print("Запуск процедуры посадки")
        self._drone.land()

class BatteryDecorator(DroneDecorator):
    def launch(self):
        if self._drone.battery_level > 20:
            super().launch()
        else:
            print(f"Низкий уровень заряда: {self._drone.battery_level}%. Запуск невозможен.")

# Паттерн "Пул объектов"
class DronePool:
    def __init__(self, size):
        self._available_drones = [Drone(f"SN{i}", "Model X", "DroneCorp") for i in range(size)]
        self._used_drones = []

    def acquire_drone(self):
        if len(self._available_drones) == 0:
            raise Exception("Нет доступных дронов")
        drone = self._available_drones.pop()
        self._used_drones.append(drone)
        return drone

    def release_drone(self, drone):
        self._used_drones.remove(drone)
        self._available_drones.append(drone)
