import json
import logging
from typing import TextIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QLabel, QSpinBox, QMessageBox, QComboBox
)

from config import Config
from .branches import branches
from .. import App

LOG_LEVELS = {
    "DEBUG": "Отладочные сообщения для разработки и тестирования.",
    "INFO": "Информационные сообщения о нормальной работе приложения.",
    "WARNING": "Предупреждения о потенциальных проблемах.",
    "ERROR": "Сообщения об ошибках, которые требуют внимания.",
    "CRITICAL": "Критические ошибки, требующие немедленного действия."
}
logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки Speedtest")
        self.setGeometry(100, 100, 600, 400)
        self.config = config
        self.inputs = {}
        logger.debug("Инициализация диалога настроек с конфигурацией: %s", self.config)
        self.setup_ui()
        self.branches = branches

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def setup_ui(self):
        """Создание интерфейса настроек."""
        layout = QVBoxLayout(self)

        # Создаем виджет вкладок
        tabs = QTabWidget()

        # Вкладки
        self.general_tab = QWidget()
        self.client_tab = QWidget()
        self.network_tab = QWidget()
        self.geo_tab = QWidget()
        self.advanced_tab = QWidget()

        # Добавляем вкладки в виджет
        tabs.addTab(self.general_tab, "Общие")
        tabs.addTab(self.client_tab, "Клиент")
        tabs.addTab(self.network_tab, "Сеть")
        tabs.addTab(self.geo_tab, "Местоположение")
        tabs.addTab(self.advanced_tab, "Дополнительно")

        # Инициализация вкладок
        self.setup_general_tab()
        self.setup_client_tab()
        self.setup_network_tab()
        self.setup_client_geography_tab()
        self.setup_advanced_tab()

        layout.addWidget(tabs)

        # Кнопки управления
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_settings)
        reset_button = QPushButton("Сбросить")
        reset_button.clicked.connect(self.reset_settings)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def setup_general_tab(self):
        """Настройки для вкладки 'Общие'."""
        form_layout = QFormLayout()

        # Данные для выпадающего списка филиалов
        branch_names = [branch.branch for branch in branches]

        # Поля, которые должны быть добавлены
        fields = [
            ("ttc.branch", "Филиал"),
            ("ttc.station", "Название станции"),
            ("app.api_key", "API-ключ"),
            ("app.part_key", "Ключ продукта")
        ]
        # if key == "connection.type":
        #     combo_box = QComboBox()
        #     combo_box.addItems(connection_types.keys())
        #     combo_box.setCurrentText(value)
        #     combo_box.setToolTip("\n".join([f"{k}: {v}" for k, v in connection_types.items()]))
        #     self.inputs[key] = combo_box
        #     form_layout.addRow(QLabel(label), combo_box)
        for key, label in fields:
            if key == "ttc.branch":
                # Если ключ соответствует филиалу, добавляем выпадающий список
                branch_selector = QComboBox()
                branch_selector.addItems(branch_names)

                # Получаем текущее значение из конфигурации
                current_branch = self.get_nested_value(self.config, key.split("."), "")

                # Устанавливаем текущее значение, если оно есть в списке филиалов
                if current_branch in branch_names:
                    branch_selector.setCurrentText(current_branch)
                else:
                    branch_selector.setCurrentIndex(0)  # Устанавливаем первый элемент, если значение не найдено

                branch_selector.setToolTip("Выберите филиал.")
                self.inputs[key] = branch_selector
                form_layout.addRow(QLabel(label), branch_selector)
            elif key == "app.part_key":
                # Если ключ соответствует ключу продукта, добавляем QLineEdit
                value = self.get_nested_value(self.config, key.split("."), "")
                part_key = App.generate_device_specific_part_key()
                input_widget = QLineEdit(value)
                input_widget.setReadOnly(True)

                if value == part_key:
                    input_widget.setText(value)
                    pass
                else:
                    input_widget.setText(part_key)
                    logger.error("Ошибка! Ключ продукта(%s) был изменен.: %s", part_key, value)
                    QMessageBox.critical(self, "Ошибка", f"Ключ продукта был изменен!")
                self.inputs[key] = input_widget
                form_layout.addRow(QLabel(label), input_widget)
            else:
                # Для остальных ключей используется обычный QLineEdit
                value = self.get_nested_value(self.config, key.split("."), "")
                input_widget = QLineEdit(value)
                input_widget.setToolTip(f"Введите {label.lower()}.")
                self.inputs[key] = input_widget
                form_layout.addRow(QLabel(label), input_widget)

        self.general_tab.setLayout(form_layout)

    def setup_client_tab(self):
        """Настройки для вкладки 'Клиент'."""
        form_layout = QFormLayout()
        logger.debug("Настройка вкладки 'Клиент'")

        fields = [
            ("client.email", "Электронная почта"),
            ("client.phone", "Телефон"),
            ("client.mac", "MAC-адрес"),
            ("client.id", "Лицевой счет"),

        ]
        for key, label in fields:
            value = self.get_nested_value(self.config, key.split("."), "")
            input_widget = QLineEdit(value)
            input_widget.setToolTip(f"Введите {label.lower()}.")
            self.inputs[key] = input_widget
            form_layout.addRow(QLabel(label), input_widget)

        self.client_tab.setLayout(form_layout)

    def setup_client_geography_tab(self):
        """Настройки для вкладки 'География клиента'."""
        form_layout = QFormLayout()

        logger.debug("Настройка вкладки 'География клиента'")

        fields = [
            ("client.region", "Регион"),
            ("client.city", "Город"),
            ("client.location.address", "Адрес"),
            ("client.name", "Организация"),
            ("client.location.latitude", "Широта"),
            ("client.location.longitude", "Долгота"),
        ]
        for key, label in fields:
            value = self.get_nested_value(self.config, key.split("."), "")
            input_widget = QLineEdit(value)
            input_widget.setToolTip(f"Введите {label.lower()}.")
            self.inputs[key] = input_widget
            form_layout.addRow(QLabel(label), input_widget)

        self.geo_tab.setLayout(form_layout)

    def setup_network_tab(self):
        """Настройки для вкладки 'Сеть'."""
        form_layout = QFormLayout()
        logger.debug("Настройка вкладки 'Сеть'")

        fields = [
            ("connection.type", "Тип подключения"),
            ("connection.login", "Логин"),
            ("connection.vlan", "VLAN"),
            ("connection.ip", "IP-адрес"),
            ("connection.tp", "Тарифная скорость"),
        ]
        connection_types = {
            "ADSL": "Интернет через телефонную линию",
            "FTTB": "Оптоволокно до здания",
            "Ethernet": "Соединение точка-точка через VPN",
            "Gpon": "Оптическая сеть гигабитного класса",
            "Wi-Fi": "Беспроводное подключение",
        }
        for key, label in fields:
            value = self.get_nested_value(self.config, key.split("."), "")
            if key == "connection.type":
                combo_box = QComboBox()
                combo_box.addItems(connection_types.keys())
                combo_box.setCurrentText(value)
                combo_box.setToolTip("\n".join([f"{k}: {v}" for k, v in connection_types.items()]))
                self.inputs[key] = combo_box
                form_layout.addRow(QLabel(label), combo_box)
            else:
                input_widget = QLineEdit(str(value))
                input_widget.setToolTip(f"Введите {label.lower()}.")
                self.inputs[key] = input_widget
                form_layout.addRow(QLabel(label), input_widget)

        self.network_tab.setLayout(form_layout)

    def setup_advanced_tab(self):
        """Настройки для вкладки 'Дополнительно'."""
        form_layout = QFormLayout()
        logger.debug("Настройка вкладки 'Дополнительно'")

        fields = [
            ("advanced.speedtest_timeout", "Тайм-аут замера (сек)", QSpinBox, (1, 3600, 30)),
            ("advanced.max_retries", "Максимальное количество попыток", QSpinBox, (1, 10, 3)),
            ("advanced.log_level", "Уровень логирования", QComboBox, LOG_LEVELS.keys()),
        ]

        for field in fields:
            key, label = field[:2]  # Первые два элемента всегда ключ и метка
            value = self.get_nested_value(self.config, key.split("."), "")

            if field[2] == QSpinBox:
                # Обработка QSpinBox с диапазоном
                spin_box = QSpinBox()
                min_value, max_value, default_value = field[3]
                spin_box.setRange(min_value, max_value)
                spin_box.setValue(int(value) if str(value).isdigit() else default_value)
                self.inputs[key] = spin_box
                form_layout.addRow(QLabel(label), spin_box)
            elif field[2] == QComboBox:
                # Обработка QComboBox
                combo_box = QComboBox()
                combo_box.addItems(field[3])
                combo_box.setCurrentText(value if value in field[3] else "INFO")
                combo_box.setToolTip("\n".join([f"{lvl}: {desc}" for lvl, desc in LOG_LEVELS.items()]))
                self.inputs[key] = combo_box
                form_layout.addRow(QLabel(label), combo_box)
            else:
                # Обработка QLineEdit по умолчанию
                input_widget = QLineEdit(value)
                self.inputs[key] = input_widget
                form_layout.addRow(QLabel(label), input_widget)

        self.advanced_tab.setLayout(form_layout)

    def reset_settings(self):
        """Сброс настроек до значений по умолчанию."""
        logger.debug("Сброс настроек")

        if QMessageBox.question(
                self, "Сброс настроек",
                "Вы уверены, что хотите сбросить настройки до значений по умолчанию?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            for key, widget in self.inputs.items():
                default_value = self.get_nested_value(self.config, key.split("."), "")
                if isinstance(widget, QLineEdit):
                    widget.setText(default_value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(default_value) if default_value.isdigit() else 30)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(default_value)

    def save_settings(self):
        """Сохранение настроек."""
        logger.debug("Сохранение настроек")

        try:
            # Создаем копию конфигурации, чтобы заполнить её значениями из виджетов
            updated_config = {}

            for key, widget in self.inputs.items():
                # Получаем значение виджета в зависимости от его типа
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QSpinBox):
                    value = widget.value()
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                else:
                    value = None  # Игнорируем неизвестные виджеты

                # Устанавливаем полученное значение в конфигурацию
                logger.debug("Сохранение поля: %s со значением: %s", key, value)
                self.set_nested_value(updated_config, key.split("."), value)

            # Записываем обновленную конфигурацию в файл
            with open(Config.CONFIG_JSON, "w", encoding="utf-8") as file:  # type: TextIO
                json.dump(updated_config, file, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Успех", "Настройки успешно сохранены.")
            self.accept()
        except Exception as e:
            logger.error("Ошибка сохранения настроек: %s", e)
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения настроек: {e}")

    def get_nested_value(self, data, keys, default=None):
        """Получение вложенного значения из словаря."""
        for key in keys:
            data = data.get(key, default) if isinstance(data, dict) else default
        logger.debug("Получено значение: %s для ключей: %s", data, keys)
        return data

    def set_nested_value(self, data, keys, value):
        """Установка вложенного значения в словарь."""
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
        logger.debug("Установлено значение: %s для ключей: %s", value, keys)
