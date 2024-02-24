#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytz
import yaml
import subprocess
import requests
import json
import os
import sys
import schedule
import platform
import time
import logging
from datetime import datetime
from pathlib import Path
import argparse
import signal
import git
from logging.handlers import RotatingFileHandler
import concurrent.futures


# Определение путей
script_directory = Path(__file__).resolve().parent
log_directory = script_directory / "logs"
log_file_name = "isl.log"


config_yaml_file_path = script_directory / "config.yaml"
config_json_file_path = script_directory / "config" / "default.json"
exe_file_path = script_directory / "bin"

#
repo_url = "https://github.com/UniTTC/isl-client"


def check_and_update():
    current_version = get_current_version()
    if check_for_updates(current_version):
        logging.info("Updating from repository...")
        update_from_repo(repo_url)
        new_version = get_current_version()
        logging.info("Update complete. New version: %s", new_version)
        if is_daemon:
            execute_speedtest()


# Добавьте эту функцию для запуска проверки обновлений каждый день в 00:00
def schedule_update_check():
    schedule.every().day.at("00:00").do(check_and_update)


def get_current_version():
    try:
        with open("VERSION", "r") as version_file:
            current_version = version_file.read().strip()
            return current_version
    except FileNotFoundError:
        logging.error(
            "The VERSION file was not found. Please provide the correct path or create a file."
        )
        return None


def update_current_version(new_version):
    with open("VERSION", "w") as version_file:
        version_file.write(new_version)


def check_for_updates(current_version):
    latest_version_url = f"{repo_url}/releases/latest"

    try:
        response = requests.get(latest_version_url)
        response.raise_for_status()
        latest_version_tag = response.url.split("/")[-1]

        if latest_version_tag != current_version:
            logging.info(f"New version available: {latest_version_tag}")
            return True
        else:
            logging.info("You have the latest version installed.")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while checking for updates: {e}")
        return False


def update_from_repo(repo_url, local_path="."):
    try:
        # Проверяем, существует ли локальный репозиторий
        if os.path.exists(os.path.join(local_path, ".git")):
            logging.info("Checking for updates...")
            # Локальный репозиторий существует, обновляем его
            repo = git.Repo(local_path)
            origin = repo.remotes.origin
            origin.fetch()
            origin.pull()
            logging.info("Update from repository completed successfully.")
        else:
            logging.info("Cloning repository...")
            repo = git.Repo.clone_from(repo_url, local_path)
            logging.info("Repository cloned successfully.")
    except git.GitCommandError as e:
        logging.error(f"Git error: {e}")


def load_configuration(config_yaml_file_path, config_json_file_path):
    if config_yaml_file_path.is_file() and config_json_file_path.is_file():
        logging.info(
            "Both YAML and JSON configuration files exist. Please use only one format.",
        )

    if config_yaml_file_path.is_file():
        with open(config_yaml_file_path, "r", encoding="utf-8") as yaml_file:
            config = yaml.safe_load(yaml_file)
    elif config_json_file_path.is_file():
        with open(config_json_file_path, "r") as json_file:
            config = json.load(json_file)
    else:
        raise FileNotFoundError("No configuration file found.")

    return config


config = load_configuration(config_yaml_file_path, config_json_file_path)


# Настройка логирования


def setup_logging():
    # Проверка существования папки "logs"
    if not log_directory.exists():
        log_directory.mkdir(parents=True, exist_ok=True)
    # Настройка логгера
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Создание форматтера
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Создание консольного обработчика (если не является демоном)
    if not is_daemon:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Создание обработчика для записи в файл с ротацией
    file_handler = RotatingFileHandler(
        log_directory / log_file_name, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


minimum_interval_s = 900
interval_s = max(config["speedtest"]["intervalSec"], minimum_interval_s)
interval_ms = interval_s * 1000


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run Speedtest and insert data into GraphQL."
    )
    parser.add_argument(
        "-d", "--daemon", action="store_true", help="Run the script as a daemon."
    )
    parser.add_argument(
        "-u", "--update", action="store_true", help="Run the script as a update."
    )

    return parser.parse_args()


# Определение временной зоны
local_tz = pytz.timezone("Asia/Almaty")


# Генерация конечной точки GraphQL
def generate_graphql_endpoint():
    graphql_config = config["graphql"]
    return f"{graphql_config['protocol']}://{graphql_config['url']}:{graphql_config['port']}{graphql_config['endpoint']}"


endpoint = generate_graphql_endpoint()


# Конвертация времени из UTC в локальное
def convert_utc_to_local(timestamp_utc):
    timestamp_datetime = datetime.strptime(timestamp_utc, "%Y-%m-%dT%H:%M:%S%z")
    timestamp_local = timestamp_datetime.astimezone(local_tz)
    return timestamp_local.strftime("%Y-%m-%dT%H:%M:%S%z")


# Получение информации о системе
def get_system_info():
    hostname = platform.node()
    os_version = platform.version()
    os_release = platform.release()
    os_type = platform.system()
    return f"{hostname} {os_type} {os_version} {os_release}"


# Вставка данных в GraphQL с логированием
def insert_data(result):
    station, branch, latitude, longitude, type, login, vlan, ip, tp = (
        config["global"]["client"]["station"],
        config["global"]["client"]["branch"],
        config["global"]["client"]["location"]["latitude"],
        config["global"]["client"]["location"]["longitude"],
        config["global"]["connection"]["type"],
        config["global"]["connection"]["login"],
        config["global"]["connection"]["vlan"],
        config["global"]["connection"]["ip"],
        config["global"]["connection"]["tp"],
    )
    runner = f"{platform.node()} {platform.system()} {platform.version()} {platform.release()}"

    byte_to_mbit = 0.000008

    timestamp, download, upload, ping, jitter = (
        convert_utc_to_local(result["timestamp"]),
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
                type:"{type}",
                login:"{login}",
                ip:"{ip}",
                tp:"{tp}"
            ) {{
                success
            }}
        }}
    """

    try:
        logging.info("Sending GraphQL request...")
        response = requests.post(endpoint, json={"query": mutation})
        response_data = response.json()["data"]["addSpeedTest"]
        logging.info("Speedtest result added.  %s", response_data)
        if not is_daemon:
            sys.exit()
    except requests.RequestException as request_error:
        logging.error("Failed to send GraphQL request: %s", request_error)
    except json.JSONDecodeError as json_error:
        logging.error("Failed to decode JSON response: %s", json_error)
    except KeyError as key_error:
        logging.error("KeyError while accessing response data: %s", key_error)
    except Exception as error:
        logging.error("An unexpected error occurred: %s", error)


# Получение команды Speedtest
def get_speedtest_command():
    if platform.system().lower() == "windows":
        return f'{exe_file_path}/{config["speedtest"]["commandStringWin"]}'
    else:
        return f'{config["speedtest"]["commandString"]}'


# Получение задержки
def get_delay(interval):
    return int(interval * (0.75 + 0.5 * (0.5 - 1) * 2))


def countdown_timer(seconds):
    # Установка обработчика сигнала Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    for remaining_time in range(seconds, 0, -1):
        time.sleep(1)
        if is_daemon and remaining_time == 1:
            execute_speedtest()


def start_speedtest_process(cmd):
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
        bufsize=1,  # line-buffered
        text=True,  # interpret output as text
    )


def handle_speedtest_output(stdout, progress_bar):
    for line in stdout:
        try:
            data = json.loads(line.strip())
            if not is_daemon:
                if data.get("type") == "result":
                    insert_data(data)
                    print(f"\rSpeedtest cmd done.   ", end="", flush=True)
                    logging.info(f"Speedtest cmd done.")
                else:
                    for key in ["ping", "download", "upload"]:
                        if data.get("type") == key:
                            progress_percentage = round(data[key]["progress"] * 100, 2)
                            print(
                                f"\r{key.capitalize()}: {progress_percentage:5.1f}%   ",
                                end="",
                                flush=True,
                            )
            else:
                if data.get("type") == "result":
                    insert_data(data)
                    print(f"\rSpeedtest cmd done.   ", end="", flush=True)
                    logging.info(f"Speedtest cmd done.")
        except json.JSONDecodeError:
            pass


def wait_for_completion(process, handle_output_func, progress_bar):
    while process.poll() is None:
        line = process.stdout.readline()
        if not line:
            break
        handle_output_func([line], progress_bar)


def execute_speedtest():
    try:
        cmd = get_speedtest_command()
        setup_logging()
        if is_update:
            check_and_update()
        logging.info("Speedtest script started.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if not is_daemon:
                process = start_speedtest_process(cmd)
                future = executor.submit(
                    wait_for_completion, process, handle_speedtest_output, None
                )
                concurrent.futures.wait([future])
            else:
                process = start_speedtest_process(cmd)
                future = executor.submit(
                    wait_for_completion, process, handle_speedtest_output, None
                )
                delay = get_delay(interval_ms)
                countdown_timer(int(delay / 1000))
                schedule_update_check()

    except Exception as error:
        logging.error("Error executing Speedtest or parsing output: %s", error)


# Установка обработчика сигнала Ctrl+C
def signal_handler(sig, frame):
    logging.info("Received Ctrl+C. Exiting gracefully...")
    sys.exit()


signal.signal(signal.SIGINT, signal_handler)

is_daemon = len(os.sys.argv) > 2 and os.sys.argv[2] == "daemon"
is_update = len(os.sys.argv) > 2 and os.sys.argv[2] == "update"


# Основной блок

if __name__ == "__main__":
    args = parse_arguments()
    is_daemon = args.daemon
    is_update = args.update

    execute_speedtest()
