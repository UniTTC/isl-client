import hashlib
import json
import logging
import subprocess
import sys
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWizard, QMessageBox

from config import Config


class App:
    """Класс для управления конфигурацией и логированием приложения."""
    CONFIG_JSON = Path(Config.CONFIG_JSON)
    LOG_DIR = Path(Config.LOG_DIR)
    LOG_FILE = Path(Config.LOG_FILE)

    def __init__(self):
        self.config = None
        self.setup_logging()

    def handle_error(self, error, user_message="Произошла ошибка"):
        """
        Централизованная обработка ошибок
        :param error: Exception or str, подробности об ошибке
        :param user_message: str, сообщение для отображения пользователю
        """
        error_details = str(error)
        logging.error(f"{user_message}: {error_details}")
        QMessageBox.critical(None, "Ошибка", f"{user_message}:\n{error_details}")
        print(f"[DEBUG] {user_message}: {error_details}")  # Для отладки в консоли

    @staticmethod
    def start_speedtest_process(cmd):
        """Запуск процесса Speedtest."""
        try:
            return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True,
                bufsize=1,
                text=True
            )
        except Exception as e:
            logging.error("Ошибка запуска процесса Speedtest: %s", e)
            return None

    @staticmethod
    def generate_device_specific_part_key():
        """
        Генерация уникального ключа устройства на основе MAC-адреса.
        Возвращает ключ в формате XXXXX-YYYYY-ZZZZZ-C, где C — контрольный символ.
        """
        try:
            mac = uuid.getnode()  # Получение MAC-адреса
            mac_hash = hashlib.sha256(str(mac).encode()).hexdigest().upper()  # Хэш в верхнем регистре

            # Формирование основного ключа
            part_key_main = f"{mac_hash[:5]}-{mac_hash[5:10]}-{mac_hash[10:15]}"

            # Вычисление контрольного символа
            checksum = sum(ord(char) for char in part_key_main if char.isalnum()) % 36
            checksum_char = chr(checksum + 48) if checksum < 10 else chr(checksum + 55)  # 0-9 или A-Z

            return f"{part_key_main}-{checksum_char}"
        except Exception as e:
            logging.error("Ошибка генерации ключа продукта: %s", e)
            return "ERROR-KEY"

    def read_config(self):
        """Чтение конфигурационного файла."""
        if not self.CONFIG_JSON.is_file():
            logging.warning("Файл конфигурации отсутствует: %s", self.CONFIG_JSON)
            return None

        try:
            with open(self.CONFIG_JSON, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logging.error("Ошибка чтения конфигурационного файла: %s", e)
            return None

    def save_config(self):
        """Сохранение конфигурации в файл."""
        try:
            with open(self.CONFIG_JSON, "w", encoding="utf-8") as file:
                json.dump(self.config, file, indent=4, ensure_ascii=False)
            logging.info("Конфигурация успешно сохранена.")
        except Exception as e:
            logging.error("Ошибка сохранения конфигурации: %s", e)
            raise RuntimeError("Не удалось сохранить файл конфигурации.") from e

    def create_default_config(self):
        """Создание дефолтной конфигурации."""
        self.config = {
            "client": {
                "name": "Default Client",
                "email": "default@example.com",
                "phone": "000-000-0000",
                "branch": "Default Branch",
                "station": "Default Station",
            },
            "connection": {
                "type": "FTTB",
                "login": "default_login",
                "vlan": 1,
                "ip": "0.0.0.0",
                "tp": 100,
            },
            "advanced": {
                "log_level": "INFO",
                "speedtest_timeout": 30,
                "max_retries": 3,
            },
        }
        logging.info("Создана дефолтная конфигурация.")
        self.save_config()

    def run_setup_wizard(self):
        """Запуск мастера настройки."""
        from .classes import SetupWizard  # Импорт SetupWizard

        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle("Fusion")  # Применение общего стиля для Fusion
        self.apply_styles(app)

        try:
            wizard = SetupWizard(self.CONFIG_JSON)
            if wizard.exec_() == QWizard.Accepted:
                QMessageBox.information(None, "Успех", "Настройки успешно сохранены.")
                self.load_config()
            else:
                QMessageBox.warning(None, "Отмена", "Мастер настройки был отменен.")
                sys.exit(1)
        except Exception as e:
            self.handle_error(e, "Ошибка при запуске мастера настройки")
            sys.exit(1)

    def load_config(self):
        """Загрузка конфигурационного файла."""
        self.config = self.read_config()
        if self.config is None:
            logging.warning("Запуск мастера настройки из-за отсутствия конфигурации.")
            self.run_setup_wizard()
        else:
            logging.info("Конфигурация успешно загружена.")

    def setup_logging(self):
        """Настройка системы логирования."""
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Логирование в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Логирование в файл
        file_handler = RotatingFileHandler(
            self.LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logging.info("Логирование настроено.")

    def start(self):
        """Точка входа в приложение."""
        try:
            self.load_config()
            logging.info("Приложение успешно запущено.")
            return self.config
        except Exception as e:
            self.handle_error(e, "Критическая ошибка")
            sys.exit(1)
