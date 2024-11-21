#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from app import App, MainApp
from config import Config


def apply_styles(app):
    """Применение стилей для интерфейса приложения."""
    app.setStyleSheet("""
        QDialog, QMainWindow {
            background-color: #f8f9fa;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }

QTabWidget::pane {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e9ecef;
    border: 1px solid #dee2e6;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    padding: 4px 4px; /* Увеличиваем внутренние отступы */
    font-weight: bold;
    color: #495057;
    min-width: 105px; /* Устанавливаем минимальную ширину вкладки */
    text-align: center; /* Выравнивание текста по центру */
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-color: #007bff;
    color: #007bff;
}

QTabBar::tab:hover {
    background-color: #f1f3f5;
}


        QGroupBox {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin-top: 10px;
            padding: 10px;
            font-weight: bold;
        }

        QLabel {
            color: #343a40;
        }

        QLineEdit, QComboBox, QSpinBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 4px;
            background-color: #ffffff;
        }

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 1px solid #007bff;
            outline: none;
        }

        QPushButton {
            background-color: #007bff;
            color: #ffffff;
            border: 1px solid #007bff;
            border-radius: 4px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #0056b3;
        }

        QPushButton:pressed {
            background-color: #004085;
        }

        QPushButton:disabled {
            background-color: #e9ecef;
            color: #adb5bd;
        }
    """)


def main():
    """Главная точка входа в приложение."""
    app_manager = App()
    try:
        config = app_manager.start()
    except Exception as e:
        print(f"Не удалось запустить приложение: {e}")
        sys.exit(1)

    # Создание экземпляра QApplication
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(Config.ICON_PATH)))

    # Применение глобальных стилей
    apply_styles(app)

    # Запуск главного окна
    window = MainApp(config)
    window.show()

    # Запуск цикла приложения
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
