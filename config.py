import json
import platform
from pathlib import Path

import yaml


class Config:
    """Конфигурация приложения."""

    # Значения по умолчанию
    APP_NAME = "ISL"
    APP_VERSION = "1.0"
    MAX_THREADS = 10
    MAX_CONNECTIONS = 50
    AUTHOR = "D.Rykov"
    AUTHOR_EMAIL = "d.rykov@ttc.kz"

    # Изначальные значения
    GRAPHQL_ENDPOINT = "/graphql"
    GRAPHQL_PROTOCOL = "http"
    GRAPHQL_URL = "isl.tgnsa.ru"
    SPEEDTEST_INTERVAL_SEC = 1200
    # Получаем текущую директорию приложения и создаем директории для логов и иконки
    BASE_DIR = Path(__file__).resolve().parent
    CONFIG_JSON = BASE_DIR / "config.json"
    LOG_DIR = BASE_DIR / "logs"
    LOG_FILE = LOG_DIR / "isl.log"
    ICON_PATH = str(BASE_DIR / "icon.ico")
    EXE_FILE_PATH = BASE_DIR / "bin"

    @staticmethod
    def get_speedtest_command():
        """Возвращает команду для запуска Speedtest в зависимости от ОС."""
        base_command = "--server-id=48175 -f json --accept-license --accept-gdpr -p"
        if platform.system().lower() == "windows":
            return f'"{Config.EXE_FILE_PATH / "speedtest.exe"}" {base_command}'
        return f"speedtest {base_command}"

    @classmethod
    def load_from_file(cls, filepath):
        """Загрузка конфигурации из файла JSON или YAML."""
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"Файл {filepath} не найден.")

        if path.suffix in [".yaml", ".yml"]:
            cls.load_from_yaml(filepath)
        elif path.suffix == ".json":
            cls.load_from_json(filepath)
        else:
            raise ValueError("Поддерживаются только файлы с расширениями .json или .yaml/.yml.")

    @classmethod
    def load_from_yaml(cls, filepath):
        """Загрузка конфигурации из YAML файла."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

                # GraphQL конфигурация
                graphql_config = data.get("graphql", {})
                cls.GRAPHQL_ENDPOINT = graphql_config.get("endpoint", cls.GRAPHQL_ENDPOINT)
                cls.GRAPHQL_PROTOCOL = graphql_config.get("protocol", cls.GRAPHQL_PROTOCOL)
                cls.GRAPHQL_URL = graphql_config.get("url", cls.GRAPHQL_URL)

                # Speedtest конфигурация
                speedtest_config = data.get("speedtest", {})
                cls.SPEEDTEST_INTERVAL_SEC = speedtest_config.get("intervalSec", cls.SPEEDTEST_INTERVAL_SEC)
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка при разборе YAML файла: {e}")

    @classmethod
    def load_from_json(cls, filepath):
        """Загрузка конфигурации из JSON файла."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

                # GraphQL конфигурация
                graphql_config = data.get("graphql", {})
                cls.GRAPHQL_ENDPOINT = graphql_config.get("endpoint", cls.GRAPHQL_ENDPOINT)
                cls.GRAPHQL_PROTOCOL = graphql_config.get("protocol", cls.GRAPHQL_PROTOCOL)
                cls.GRAPHQL_URL = graphql_config.get("url", cls.GRAPHQL_URL)

                # Speedtest конфигурация
                speedtest_config = data.get("speedtest", {})
                cls.SPEEDTEST_INTERVAL_SEC = speedtest_config.get("intervalSec", cls.SPEEDTEST_INTERVAL_SEC)
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка при разборе JSON файла: {e}")

    @classmethod
    def save_to_file(cls, filepath):
        """Сохранение текущей конфигурации в файл JSON или YAML."""
        path = Path(filepath)
        config_data = {
            "graphql": {
                "endpoint": cls.GRAPHQL_ENDPOINT,
                "protocol": cls.GRAPHQL_PROTOCOL,
                "url": cls.GRAPHQL_URL,
            },
            "speedtest": {
                "intervalSec": cls.SPEEDTEST_INTERVAL_SEC,
            },
        }

        if path.suffix in [".yaml", ".yml"]:
            with open(filepath, "w", encoding="utf-8") as file:
                yaml.dump(config_data, file, allow_unicode=True, default_flow_style=False)
        elif path.suffix == ".json":
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(config_data, file, ensure_ascii=False, indent=4)
        else:
            raise ValueError("Поддерживаются только файлы с расширениями .json или .yaml/.yml.")

    @property
    def speedtest_command(self):
        """Динамическое свойство для команды Speedtest."""
        return self.get_speedtest_command()
