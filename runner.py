#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from colorama import init, Fore, Style
# Инициализация colorama для поддержки цветного вывода в консоли
init()

# Определение путей
script_directory = Path(__file__).resolve().parent
log_directory = script_directory / "logs"
log_file_name = "isl.log"

config_yaml_file_path = script_directory / "config.yaml"
config_json_file_path = script_directory / "config" / "default.json"
exe_file_path = script_directory / "bin"
speedtest_running = False


def load_configuration(yaml_path, json_path):
    if yaml_path.is_file() and json_path.is_file():
        logging.warning("Both YAML and JSON configuration files exist. Use only one format.")
    if yaml_path.is_file():
        with open(yaml_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    elif json_path.is_file():
        with open(json_path, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError("Configuration file not found.")


config = load_configuration(config_yaml_file_path, config_json_file_path)

def verbose(name, var, verbose=False):
    if verbose:
        if isinstance(var, str):
            is_logical_green = var.lower() in ['true', 'success', '200']
            is_logical_red = var.lower() in ['false', 'error','Failed']
            color = Fore.GREEN if is_logical_green else (Fore.RED if is_logical_red else Fore.YELLOW)
        else:
            color = Fore.GREEN if var else Fore.RED
        print(f"{Fore.CYAN}{name}{color}{var}{Style.RESET_ALL}")


def human_time_value(time):
    return datetime.fromtimestamp(time)


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
    parser.add_argument("-v", "--verbose", action="store_true", help="Run the script as a verbose mode.")
    return parser.parse_args()


# Определение временной зоны
local_tz = pytz.timezone("Asia/Almaty")


# Генерация конечной точки GraphQL
def generate_graphql_endpoint():
    graphql_config = config["graphql"]
    return f"{graphql_config['protocol']}://{graphql_config['url']}{graphql_config['endpoint']}"


endpoint = generate_graphql_endpoint()


def insert_data(result):
    verbose("Speedtest result:", result, verbose=verbose_mode)

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
    verbose("Runner info:", runner, verbose=verbose_mode)

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
    verbose("Mutation:",mutation, verbose=verbose_mode)

    timeout_seconds = 10  # Установка таймаута в 10 секунд

    try:
        logging.info("Sending a GraphQL request over HTTP...")
        verbose("GraphQL Endpoint:",endpoint, verbose=verbose_mode)

        response = requests.post(endpoint, json={"query": mutation}, timeout=timeout_seconds)
        verbose("Response:",response, verbose=verbose_mode)

        response.raise_for_status()
        response_data = response.json()["data"]["addSpeedTest"]
        verbose("Response data:",response_data, verbose=verbose_mode)

        logging.info("Speedtest result added: %s", response_data)

        if not is_daemon:
            sys.exit()
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        logging.warning("Error attempting to send request via HTTP: %s. Switching to HTTPS...", e)
        try:
            https_endpoint = endpoint.replace("http://", "https://")
            verbose("GraphQL Endpoint:",https_endpoint, verbose=verbose_mode)

            logging.info("Sending GraphQL request via HTTPS...")
            response = requests.post(https_endpoint, json={"query": mutation}, timeout=timeout_seconds)
            verbose("Response:",response, verbose=verbose_mode)
            response.raise_for_status()
            response_data = response.json()["data"]["addSpeedTest"]
            verbose("Response data:",response_data, verbose=verbose_mode)

            logging.info("Speedtest result added: %s", response_data)

            if not is_daemon:
                sys.exit()
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logging.error("Error when trying to send a request via HTTPS: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


def get_speedtest_command():
    comand = str(exe_file_path / config["speedtest"]["commandStringWin"]) if platform.system().lower() == "windows" else config["speedtest"]["commandString"]
    verbose("Speedtest command:",comand, verbose=verbose_mode)
    return comand

# def countdown_timer(interval):
#     signal.signal(signal.SIGINT, signal_handler)

#     scheduler = sched.scheduler(time.time, time.sleep)
#     verbose("Daemon scheduler:",scheduler, verbose=verbose_mode)

#     next_call = time.time()
#     # Преобразование временной метки в объект datetime
#     next_call_datetime = datetime.fromtimestamp(next_call)
#     verbose(f"Daemon next_call:{next_call_datetime} = ",next_call, verbose=verbose_mode)

#     while True:
#         scheduler.enterabs(next_call, 1, execute_speedtest, ())
#         next_call += interval
#         time.sleep(1)


def countdown_timer(interval):
    signal.signal(signal.SIGINT, signal_handler)

    scheduler = sched.scheduler(time.time, time.sleep)
    verbose("Daemon scheduler:", scheduler, verbose=verbose_mode)

    next_call = time.time()
    h_nc1 = human_time_value(next_call)
    verbose(f"Daemon next_call:{h_nc1} = ", next_call, verbose=verbose_mode)

    while True:
        # Установите время следующего запуска
        next_call += interval
        h_nc = human_time_value(next_call)
        verbose(f"Daemon next_call:{h_nc} = ", next_call, verbose=verbose_mode)
        
        # Подождите до времени следующего запуска
        time_to_wait = max(0, next_call - time.time())
        time.sleep(time_to_wait)

        # Возвращаем True по достижению интервала
        print("Interval reached!")
        return True


def start_speedtest_process(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1, text=True)


def handle_speedtest_output(stdout):
    for line in stdout:
        try:
            data = json.loads(line.strip())
            verbose("Speedtest Data:",data, verbose=verbose_mode)

            # verbose("Speedtest Data:", data.get("type") == "result", data, verbose=verbose_mode)
            if data.get("type") == "result":
                insert_data(data)
                logging.info("Speedtest sucess.")
        except json.JSONDecodeError:
            pass


def wait_for_completion(process, handle_output_func):
    while process.poll() is None:
        line = process.stdout.readline()
        if not line:
            break
        handle_output_func([line])


def execute_speedtest():
    verbose("Run is DAEMON:",is_daemon, verbose=verbose_mode)
    verbose("Run is VERBOSE:",verbose_mode, verbose=verbose_mode)
    try:
        cmd = get_speedtest_command()
        setup_logging()
        logging.info("Speedtest script running.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            process = start_speedtest_process(cmd)
            future = executor.submit(wait_for_completion, process, handle_speedtest_output)
            concurrent.futures.wait([future])
            if is_daemon:
                if countdown_timer(interval_s):
                    execute_speedtest()
    except Exception as e:
        logging.error("Error running Speedtest or parsing output: %s", e)


def signal_handler(sig, frame):
    logging.info("Ctrl+C signal received. Shutting down...")
    sys.exit()


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    args = parse_arguments()
    is_daemon = args.daemon

    verbose_mode  = args.verbose

    execute_speedtest()
