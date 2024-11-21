import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit,
    QFormLayout, QComboBox, QSpinBox, QMessageBox
)

from config import Config
from .branches import branches
from .. import App


class SetupWizard(QWizard):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Мастер настройки приложения")
        self.setWizardStyle(QWizard.ModernStyle)
        self.config_path = config_path
        self.config = {}

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Добавление страниц мастера
        try:
            self.addPage(self.create_intro_page())
            self.addPage(self.create_general_settings_page())
            self.addPage(self.create_client_settings_page())
            self.addPage(self.create_client_geographic_location_page())
            self.addPage(self.create_network_settings_page())
            self.addPage(self.create_advanced_settings_page())
            self.addPage(self.create_finish_page())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании мастера: {e}")

    def create_intro_page(self):
        """Создание стартовой страницы."""
        page = QWizardPage()
        page.setTitle("Добро пожаловать")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Этот мастер поможет вам настроить приложение."))
        layout.addWidget(QLabel("Нажмите 'Далее' для продолжения."))
        page.setLayout(layout)
        return page

    def create_general_settings_page(self):
        """Создание общих настроек."""
        page = QWizardPage()
        page.setTitle("Общие настройки")
        layout = QFormLayout()
        branch_names = [branch.branch for branch in branches]

        self.ttc_branch_input = QComboBox()
        self.ttc_branch_input.addItems(branch_names)

        self.ttc_station_input = QLineEdit()
        self.app_part_key_input = QLineEdit()
        part_key = App.generate_device_specific_part_key()
        self.app_part_key_input.setText(part_key)
        self.app_part_key_input.setReadOnly(True)

        self.app_author_input = QLineEdit(Config.AUTHOR)
        self.app_author_input.setReadOnly(True)

        self.app_email_input = QLineEdit(Config.AUTHOR_EMAIL)
        self.app_email_input.setReadOnly(True)

        self.app_version_input = QLineEdit(Config.APP_VERSION)
        self.app_version_input.setReadOnly(True)

        layout.addRow("Филиал:", self.ttc_branch_input)
        layout.addRow("Станция:", self.ttc_station_input)
        layout.addRow("Ключ приложения:", self.app_part_key_input)
        layout.addRow("Версия:", self.app_version_input)
        layout.addRow("Автор:", self.app_author_input)
        layout.addRow("Электронная почта:", self.app_email_input)

        page.setLayout(layout)
        return page

    def create_client_settings_page(self):
        """Создание страницы настроек клиента."""
        page = QWizardPage()
        page.setTitle("Настройки клиента")
        layout = QFormLayout()

        self.client_name_input = QLineEdit()
        self.client_email_input = QLineEdit()
        self.client_phone_input = QLineEdit()
        self.client_id_input = QLineEdit()

        layout.addRow("Наименование организации:", self.client_name_input)
        layout.addRow("Электронная почта:", self.client_email_input)
        layout.addRow("Телефон:", self.client_phone_input)
        layout.addRow("Лицевой счет:", self.client_id_input)

        page.setLayout(layout)
        return page

    def create_client_geographic_location_page(self):
        """Создание полей для координат клиента."""
        page = QWizardPage()
        page.setTitle("Географическое расположение")
        layout = QFormLayout()

        self.client_region_input = QLineEdit()
        self.client_city_input = QLineEdit()
        self.client_location_address_input = QLineEdit()
        self.client_location_latitude_input = QLineEdit()
        self.client_location_longitude_input = QLineEdit()

        layout.addRow("Регион:", self.client_region_input)
        layout.addRow("Город:", self.client_city_input)
        layout.addRow("Адрес:", self.client_location_address_input)
        layout.addRow("Широта:", self.client_location_latitude_input)
        layout.addRow("Долгота:", self.client_location_longitude_input)

        page.setLayout(layout)
        return page

    def create_network_settings_page(self):
        """Создание страницы сетевых настроек."""
        page = QWizardPage()
        page.setTitle("Настройки сети")
        layout = QFormLayout()

        self.connection_type_input = QComboBox()
        self.connection_type_input.addItems(["FTTB", "ADSL", "Gpon", "Ethernet", "Wi-Fi"])
        self.connection_login_input = QLineEdit()
        self.client_mac_address_input = QLineEdit()
        self.connection_vlan_input = QLineEdit()
        self.connection_ip_input = QLineEdit()
        self.connection_tp_input = QLineEdit()

        layout.addRow("Тип подключения:", self.connection_type_input)
        layout.addRow("Логин:", self.connection_login_input)
        layout.addRow("MAC-адрес:", self.client_mac_address_input)
        layout.addRow("VLAN:", self.connection_vlan_input)
        layout.addRow("IP-адрес:", self.connection_ip_input)
        layout.addRow("Тарифная скорость (Мбит/с):", self.connection_tp_input)

        page.setLayout(layout)
        return page

    def create_advanced_settings_page(self):
        """Создание страницы дополнительных настроек."""
        page = QWizardPage()
        page.setTitle("Дополнительные настройки")
        layout = QFormLayout()

        self.log_level_input = QComboBox()
        self.log_level_input.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.speedtest_timeout_input = QSpinBox()
        self.speedtest_timeout_input.setRange(1, 3600)
        self.max_retries_input = QSpinBox()
        self.max_retries_input.setRange(1, 10)
        self.app_api_key_input = QLineEdit()

        layout.addRow("Уровень логирования:", self.log_level_input)
        layout.addRow("Тайм-аут замера (сек):", self.speedtest_timeout_input)
        layout.addRow("Максимальное количество попыток:", self.max_retries_input)
        layout.addRow("API-ключ приложения:", self.app_api_key_input)

        page.setLayout(layout)
        return page

    def create_finish_page(self):
        """Создание финальной страницы."""
        page = QWizardPage()
        page.setTitle("Завершение настройки")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Настройка завершена. Нажмите 'Готово', чтобы сохранить настройки."))
        page.setLayout(layout)
        return page

    def accept(self):
        """Сохранение настроек при завершении мастера."""
        try:
            self.config = {
                "ttc": {
                    "branch": self.ttc_branch_input.currentText(),
                    "station": self.ttc_station_input.text(),
                },
                "app": {
                    "part_key": self.app_part_key_input.text(),
                    "api_key": self.app_api_key_input.text(),
                },
                "client": {
                    "name": self.client_name_input.text(),
                    "email": self.client_email_input.text(),
                    "phone": self.client_phone_input.text(),
                    "region": self.client_region_input.text(),
                    "city": self.client_city_input.text(),
                    "location": {
                        "address": self.client_location_address_input.text(),
                        "latitude": self.client_location_latitude_input.text(),
                        "longitude": self.client_location_longitude_input.text()
                    },
                    "mac": self.client_mac_address_input.text(),
                    "id": self.client_id_input.text()
                },
                "connection": {
                    "type": self.connection_type_input.currentText(),
                    "login": self.connection_login_input.text(),
                    "vlan": self.connection_vlan_input.text(),
                    "ip": self.connection_ip_input.text(),
                    "tp": self.connection_tp_input.text(),
                },
                "advanced": {
                    "log_level": self.log_level_input.currentText(),
                    "speedtest_timeout": self.speedtest_timeout_input.value(),
                    "max_retries": self.max_retries_input.value(),
                }
            }

            # Сохранение конфигурации в файл
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(self.config, file, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Успех", "Настройки успешно сохранены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения настроек: {e}")
        super().accept()
