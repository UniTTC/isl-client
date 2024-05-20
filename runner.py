import sched
import pytz
import yaml
import subprocess
import requests
import json
import os
import sys
import platform
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
import argparse
import signal
from logging.handlers import RotatingFileHandler
import concurrent.futures


# Определение путей
script_directory = Path(__file__).resolve().parent
log_directory = script_directory / "logs"
log_file_name = "isl.log"

config_yaml_file_path = script_directory / "config.yaml"
config_json_file_path = script_directory / "config" / "default.json"
exe_file_path = script_directory / "bin"


def load_configuration(yaml_path, json_path):
    if yaml_path.is_file() and json_path.is_file():
        logging.warning("Оба файла конфигурации YAML и JSON существуют. Используйте только один формат.")
    if yaml_path.is_file():
        with open(yaml_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    elif json_path.is_file():
        with open(json_path, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError("Файл конфигурации не найден.")


config = load_configuration(config_yaml_file_path, config_json_file_path)


# Настройка логирования
def setup_logging():
    if not log_directory.exists():
        log_directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    if not is_daemon:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(log_directory / log_file_name, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


minimum_interval_s = 900
interval_s = max(config["speedtest"]["intervalSec"], minimum_interval_s)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run Speedtest and insert data into GraphQL.")
    parser.add_argument("-d", "--daemon", action="store_true", help="Run the script as a daemon.")
    return parser.parse_args()


# Определение временной зоны
local_tz = pytz.timezone("Asia/Almaty")


# Генерация конечной точки GraphQL
def generate_graphql_endpoint():
    graphql_config = config["graphql"]
    return f"{graphql_config['protocol']}://{graphql_config['url']}:{graphql_config['port']}{graphql_config['endpoint']}"


endpoint = generate_graphql_endpoint()


def insert_data(result):
    global_config = config["global"]
    client = global_config["client"]
    connection = global_config["connection"]

    station, branch, latitude, longitude, conn_type, login, vlan, ip, tp = (
        client["station"],
        client["branch"],
        client["location"]["latitude"],
        client["location"]["longitude"],
        connection["type"],
        connection["login"],
        connection["vlan"],
        connection["ip"],
        connection["tp"],
    )
    runner = f"{platform.node()} {platform.system()} {platform.version()} {platform.release()}"

    byte_to_mbit = 0.000008

    timestamp, download, upload, ping, jitter = (
        result["timestamp"],
        result["download"]["bandwidth"] * byte_to_mbit,
        result["upload"]["bandwidth"] * byte_to_mbit,
        result["ping"]["latency"],
        result["ping"]["jitter"],
    )

    mutation = f"""
        mutation AddSpeedTest {{
            addSpeedTest(
                date: "{timestamp}",
                download: "{download}",
                upload: "{upload}",
                ping: "{ping}",
                jitter: "{jitter}",
                station: "{station}",
                branch: "{branch}",
                vlan: "{vlan}",
                runner: "{runner}",
                latitude:"{latitude}",
                longitude:"{longitude}",
                type:"{conn_type}",
                login:"{login}",
                ip:"{ip}",
                tp:"{tp}"
            ) {{
                success
            }}
        }}
    """

    timeout_seconds = 10  # Установка таймаута в 10 секунд

    try:
        logging.info("Отправка запроса GraphQL через HTTP...")
        response = requests.post(endpoint, json={"query": mutation}, timeout=timeout_seconds)
        response.raise_for_status()
        response_data = response.json()["data"]["addSpeedTest"]
        logging.info("Результат Speedtest добавлен: %s", response_data)
        if not is_daemon:
            sys.exit()
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        logging.warning("Ошибка при попытке отправить запрос через HTTP: %s. Переход на HTTPS...", e)
        try:
            https_endpoint = endpoint.replace("http://", "https://")
            logging.info("Отправка запроса GraphQL через HTTPS...")
            response = requests.post(https_endpoint, json={"query": mutation}, timeout=timeout_seconds)
            response.raise_for_status()
            response_data = response.json()["data"]["addSpeedTest"]
            logging.info("Результат Speedtest добавлен: %s", response_data)
            if not is_daemon:
                sys.exit()
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logging.error("Ошибка при попытке отправить запрос через HTTPS: %s", e)
    except Exception as e:
        logging.error("Неожиданная ошибка: %s", e)


def get_speedtest_command():
    return str(exe_file_path / config["speedtest"]["commandStringWin"]) if platform.system().lower() == "windows" else config["speedtest"]["commandString"]


def countdown_timer(interval):
    signal.signal(signal.SIGINT, signal_handler)

    scheduler = sched.scheduler(time.time, time.sleep)
    next_call = time.time()

    while True:
        scheduler.enterabs(next_call, 1, execute_speedtest, ())
        next_call += interval
        time.sleep(1)


def start_speedtest_process(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1, text=True)


def handle_speedtest_output(stdout):
    for line in stdout:
        try:
            data = json.loads(line.strip())
            if data.get("type") == "result":
                insert_data(data)
                logging.info("Speedtest завершён.")
        except json.JSONDecodeError:
            pass


def wait_for_completion(process, handle_output_func):
    while process.poll() is None:
        line = process.stdout.readline()
        if not line:
            break
        handle_output_func([line])


def execute_speedtest():
    try:
        cmd = get_speedtest_command()
        setup_logging()
        logging.info("Скрипт Speedtest запущен.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            process = start_speedtest_process(cmd)
            future = executor.submit(wait_for_completion, process, handle_speedtest_output)
            concurrent.futures.wait([future])
            if is_daemon:
                countdown_timer(interval_s)
    except Exception as e:
        logging.error("Ошибка при выполнении Speedtest или разборе вывода: %s", e)


def signal_handler(sig, frame):
    logging.info("Получен сигнал Ctrl+C. Завершаем работу...")
    sys.exit()


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    args = parse_arguments()
    is_daemon = args.daemon
    execute_speedtest()
