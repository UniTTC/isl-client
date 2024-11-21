import json
import logging
from threading import Thread

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, \
    QMessageBox, QSystemTrayIcon, QMenu, QAction, QApplication, QTextEdit, QSplitter, QDockWidget, QToolBar

from app.classes.settings import SettingsDialog
from config import Config

logger = logging.getLogger(__name__)


class MainApp(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle("Speedtest Client")
        self.setGeometry(100, 100, 800, 400)
        self.icon = QIcon(Config.ICON_PATH)
        self.setWindowIcon(self.icon)

        self.config = config
        self.running = False
        self.speedtest_process = None

        self.setup_ui()
        self.setup_menu()
        self.setup_tray_icon()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def hide_vbox_layout(self, layout):
        """Скрыть все виджеты внутри QVBoxLayout."""
        for i in range(layout.count()):
            item = layout.itemAt(i).widget()
            if item is not None:
                item.hide()

    def setup_ui(self):
        """Настройка основного интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Левая часть с метриками и кнопками
        left_layout = QVBoxLayout()
        self.download_label = QLabel("Download Speed: - Mbps")
        self.upload_label = QLabel("Upload Speed: - Mbps")
        self.ping_label = QLabel("Ping: - ms")
        self.jitter_label = QLabel("Jitter: - ms")

        start_button = QPushButton("Start Speedtest")
        start_button.clicked.connect(self.start_speedtest)

        stop_button = QPushButton("Stop Speedtest")
        stop_button.clicked.connect(self.stop_speedtest)

        left_layout.addWidget(self.download_label)
        left_layout.addWidget(self.upload_label)
        left_layout.addWidget(self.ping_label)
        left_layout.addWidget(self.jitter_label)
        left_layout.addStretch()
        left_layout.addWidget(start_button)
        left_layout.addWidget(stop_button)

        # Правая часть: DockWidget для логов
        dock = QDockWidget("Log Output", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock_widget = QWidget()
        dock_layout = QVBoxLayout(dock_widget)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        dock_layout.addWidget(self.log_output)
        dock_widget.setLayout(dock_layout)

        # Устанавливаем содержимое в док-виджет
        dock.setWidget(dock_widget)

        # Добавляем док-виджет в главное окно
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # Панель инструментов
        toolbar = QToolBar("Основная панель", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Добавляем действия
        action_open = QAction("Открыть", self)
        action_open.triggered.connect(lambda: self.append_log("Открыть нажат!"))

        action_save = QAction("Сохранить", self)
        action_save.triggered.connect(lambda: self.append_log("Сохранить нажат!"))


        action_clear_log = QAction("Очистить логи", self)
        action_clear_log.triggered.connect(self.clear_log)

        toolbar.addAction(action_clear_log)

        toolbar.addAction(action_open)
        toolbar.addAction(action_save)

        # Добавляем разделитель
        toolbar.addSeparator()

        # Добавляем виджет
        toolbar.addWidget(QLabel("Панель управления"))

        # Компоновка
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        main_layout.addWidget(left_widget)

    def setup_menu(self):
        """Настройка меню."""
        file_menu = self.menuBar().addMenu("Файл")

        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)



        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_tray_icon(self):
        """Настройка иконки в системном трее."""
        self.tray_icon = QSystemTrayIcon(self.icon, self)
        self.tray_menu = QMenu(self)

        toggle_action = QAction("Показать/Скрыть", self)
        toggle_action.triggered.connect(self.toggle_window)

        start_action = QAction("Начать замер", self)
        start_action.triggered.connect(self.start_speedtest)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(QApplication.quit)

        self.tray_menu.addAction(toggle_action)
        self.tray_menu.addAction(start_action)
        self.tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        self.tray_icon.showMessage(
            "Приложение свернуто",
            "Иконка находится в системном трее.",
            QSystemTrayIcon.Information,
            3000
        )

    def toggle_window(self):
        """Переключение видимости окна."""
        self.setVisible(not self.isVisible())

    @pyqtSlot()
    def start_speedtest(self):
        """Запуск замера скорости."""
        if self.running:
            QMessageBox.information(self, "Информация", "Speedtest уже выполняется.")
            return

        self.running = True
        self.append_log("Запуск Speedtest...")

        try:
            # Запуск Speedtest в отдельном потоке
            thread = Thread(target=self.run_speedtest, daemon=True)
            thread.start()
        except Exception as e:
            self.append_log(f"Ошибка запуска Speedtest: {e}")
            self.handle_error(e, "Ошибка запуска Speedtest")
            self.running = False

    @pyqtSlot()
    def stop_speedtest(self):
        """Остановка замера скорости."""
        if not self.running:
            QMessageBox.warning(self, "Предупреждение", "Speedtest не выполняется.")
            return

        self.append_log("Остановка Speedtest...")
        self.running = False

        try:
            if self.speedtest_process:
                self.speedtest_process.terminate()  # Завершение процесса Speedtest
                self.speedtest_process = None
                self.append_log("Speedtest успешно остановлен.")
        except Exception as e:
            self.append_log(f"Ошибка при остановке Speedtest: {e}")

    def run_speedtest(self):
        """Запуск теста скорости."""
        from app import App

        cmd = Config().speedtest_command  # Получаем команду для запуска Speedtest

        try:
            # Запускаем процесс Speedtest
            self.speedtest_process = App.start_speedtest_process(cmd)
            if not self.speedtest_process:
                raise RuntimeError("Не удалось запустить процесс Speedtest.")

            # Чтение вывода процесса построчно
            for line in iter(self.speedtest_process.stdout.readline, ""):
                line = line.strip()
                if line:
                    print(line.strip())
                    # self.append_log(line)  # Логируем вывод
                    self.handle_speedtest_output(line)  # Обрабатываем вывод

            # Проверка завершения процесса
            return_code = self.speedtest_process.wait()
            if return_code != 0:
                raise RuntimeError(
                    f"Процесс Speedtest завершился с кодом ошибки {return_code}."
                )
            self.append_log("Speedtest успешно завершен.")
        except FileNotFoundError:
            self.append_log("Speedtest CLI не найден. Проверьте путь в настройках.")
            self.handle_error(
                FileNotFoundError("Speedtest CLI не найден."),
                "Speedtest CLI не найден. Убедитесь, что он установлен.",
            )
        except RuntimeError as e:
            self.append_log(f"Ошибка выполнения Speedtest: {e}")
        except Exception as e:
            self.append_log(f"Произошла неожиданная ошибка: {e}")
        finally:
            if self.speedtest_process and self.speedtest_process.poll() is None:
                self.speedtest_process.terminate()  # Завершаем процесс, если он еще работает
            self.running = False
            self.speedtest_process = None
            self.append_log("Speedtest завершен.")

    def handle_speedtest_output(self, line):
        try:
            data = json.loads(line)

            # Обработка известных типов
            if data.get("type") == "download":
                bandwidth_mbps = data["download"]["bandwidth"] * 0.000008  # Преобразование в Мбит/с
                self.append_log(f"Загрузка: {bandwidth_mbps:.2f} Мбит/с")
                self.update_metrics(download=bandwidth_mbps)
            elif data.get("type") == "upload":
                bandwidth_mbps = data["upload"]["bandwidth"] * 0.000008  # Преобразование в Мбит/с
                self.append_log(f"Загрузка: {bandwidth_mbps:.2f} Мбит/с")
                self.update_metrics(upload=bandwidth_mbps)
            elif data.get("type") == "result":
                download = data["download"]["bandwidth"] * 0.000008  # Конвертация в Мбит/с
                upload = data["upload"]["bandwidth"] * 0.000008
                ping = data["ping"]["latency"]
                jitter = data["ping"].get("jitter", 0)

                self.update_metrics(download, upload, ping, jitter)

            elif data.get("type") == "testStart":
                # Логирование информации о начале теста
                isp = data.get("isp", "Неизвестно")
                server_info = data.get("server", {})
                server_name = server_info.get("name", "Неизвестный сервер")
                location = server_info.get("location", "Неизвестное местоположение")

                self.append_log(f"Начало теста: провайдер {isp}, сервер {server_name} ({location})")

            elif data.get("type") == "ping":
                # Обработка данных ping
                latency = data["ping"]["latency"]
                jitter = data["ping"]["jitter"]
                self.append_log(f"Ping: {latency:.2f} ms, Jitter: {jitter:.2f} ms")
                self.update_metrics(ping=latency, jitter=jitter)  # Обновляем только Ping/Jitter


            else:
                # Логирование неизвестного типа
                self.append_log(f"Неизвестный тип данных: {line}")
                logging.info(f"Неизвестный тип данных: {line}")

        except json.JSONDecodeError as e:
            self.append_log(f"Ошибка парсинга JSON: {line}")
            self.handle_error(e, "Ошибка парсинга JSON")

    def update_metrics(self, download=None, upload=None, ping=None, jitter=None):
        try:
            # Обновление метрик, если они переданы
            if download is not None:
                if not isinstance(download, (int, float)):
                    raise ValueError("Некорректное значение для Download Speed")
                self.download_label.setText(f"Download Speed: {download:.2f} Mbps")

            if upload is not None:
                if not isinstance(upload, (int, float)):
                    raise ValueError("Некорректное значение для Upload Speed")
                self.upload_label.setText(f"Upload Speed: {upload:.2f} Mbps")

            if ping is not None:
                if not isinstance(ping, (int, float)):
                    raise ValueError("Некорректное значение для Ping")
                self.ping_label.setText(f"Ping: {ping:.2f} ms")

            if jitter is not None:
                if not isinstance(jitter, (int, float)):
                    raise ValueError("Некорректное значение для Jitter")
                self.jitter_label.setText(f"Jitter: {jitter:.2f} ms")
        except ValueError as ve:
            # Логирование ошибки некорректных значений
            logging.error(f"Некорректное значение метрики: {ve}")
        except Exception as e:
            # Логирование общей ошибки
            logging.error(f"Ошибка при обновлении метрик: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить метрики:\n{e}")

    def append_log(self, message):
        try:
            # Проверяем, является ли сообщение строкой или допустимым JSON-объектом
            if isinstance(message, str):
                try:
                    # Попробуем парсить сообщение как JSON
                    parsed_message = json.loads(message)
                    formatted_message = self.format_log_message(parsed_message)
                except json.JSONDecodeError:
                    # Если это не JSON, оставляем сообщение как есть
                    formatted_message = message
            else:
                formatted_message = str(message)

            # Логируем сообщение
            logging.info(formatted_message)

            # Добавляем сообщение в лог вывода
            self.log_output.append(formatted_message)
            self.log_output.ensureCursorVisible()

        except Exception as e:
            # Логируем ошибку
            logging.error(f"Ошибка при добавлении сообщения в лог: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить сообщение в лог:\n{e}")

    def format_log_message(self, message):
        """
        Форматирует JSON-сообщение в человекопонятный вид.

        :param message: dict - Распарсенное JSON-сообщение.
        :return: str - Форматированное сообщение.
        """
        try:
            if "type" in message:
                message_type = message.get("type", "unknown").capitalize()
                timestamp = message.get("timestamp", "unknown")
                details = []

                # Форматируем разные типы сообщений
                if message_type == "Download":
                    download = message.get("download", {})
                    bandwidth = download.get("bandwidth", 0) / 1_000_000  # Преобразуем в Mbps
                    details.append(f"Download Speed: {bandwidth:.2f} Mbps")
                    details.append(f"Bytes: {download.get('bytes', 0)}")
                    details.append(f"Elapsed: {download.get('elapsed', 0)} ms")
                    details.append(f"Latency: {download.get('latency', {}).get('iqm', 'N/A')} ms")
                elif message_type == "Upload":
                    upload = message.get("upload", {})
                    bandwidth = upload.get("bandwidth", 0) / 1_000_000  # Преобразуем в Mbps
                    details.append(f"Upload Speed: {bandwidth:.2f} Mbps")
                    details.append(f"Bytes: {upload.get('bytes', 0)}")
                    details.append(f"Elapsed: {upload.get('elapsed', 0)} ms")
                elif message_type == "Ping":
                    ping = message.get("ping", {})
                    details.append(f"Ping: {ping.get('latency', 'N/A')} ms")
                    details.append(f"Jitter: {ping.get('jitter', 'N/A')} ms")

                # Собираем форматированное сообщение
                formatted_message = f"{timestamp} - {message_type}: " + ", ".join(details)
                return formatted_message

            # Если ключ "type" отсутствует, возвращаем сырой JSON
            return json.dumps(message, indent=4, ensure_ascii=False)

        except Exception as e:
            logging.error(f"Ошибка при форматировании сообщения: {e}")
            return str(message)

    def open_settings(self):
        """Открытие окна настроек."""
        try:
            dialog = SettingsDialog(self.config, self)
            if dialog.exec_():
                QMessageBox.information(self, "Успех", "Настройки обновлены.")
        except Exception as e:
            logger.error("Ошибка при открытии настроек: %s", e)
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при открытии окна настроек: {e}")

    def clear_log(self):
        """Очистка логов."""
        try:
            self.log_output.clear()  # Очищаем виджет лога
            logging.info("Лог был успешно очищен.")
        except Exception as e:
            logging.error(f"Ошибка при очистке логов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось очистить логи:\n{e}")

    def on_tray_icon_activated(self, reason):
        """Обработка активации иконки в системном трее."""
        try:
            if reason == QSystemTrayIcon.Trigger:
                self.toggle_window()
                logging.info("Иконка в системном трее была активирована (Trigger).")
            elif reason == QSystemTrayIcon.Context:
                logging.info("Контекстное меню иконки в системном трее вызвано.")
            else:
                logging.debug(f"Иконка в системном трее активирована с неизвестной причиной: {reason}")
        except Exception as e:
            logging.error(f"Ошибка при обработке активации иконки в системном трее: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при активации иконки в системном трее:\n{e}")

    def closeEvent(self, event):
        """Обработка закрытия приложения."""
        try:
            logger.info("Приложение закрывается. Очистка ресурсов.")

            # Скрываем иконку из системного трея
            if self.tray_icon:
                self.tray_icon.hide()
                logger.info("Иконка системного трея успешно скрыта.")

            # Проверяем и завершаем процесс Speedtest, если он запущен
            if self.speedtest_process and self.speedtest_process.poll() is None:
                self.speedtest_process.terminate()
                self.speedtest_process.wait()
                logger.info("Процесс Speedtest успешно завершен.")

            # Сбрасываем состояние
            self.running = False
            self.speedtest_process = None

            # Записываем финальное сообщение в лог
            logger.info("Приложение закрыто корректно.")
            super().closeEvent(event)

        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при закрытии приложения:\n{e}")
            event.ignore()  # Не позволяем закрыть приложение в случае ошибки
