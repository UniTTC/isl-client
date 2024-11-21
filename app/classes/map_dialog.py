from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSignal


class MapDialog(QDialog):
    coordinatesSelected = pyqtSignal(float, float)  # Сигнал для передачи координат

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор координат")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Виджет карты
        self.map_view = QWebEngineView()
        self.map_view.setHtml(self.get_map_html())
        layout.addWidget(self.map_view)

        # Кнопка для закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # Связываем JavaScript с Python
        self.map_view.page().javaScriptConsoleMessage = self.handle_js_console_message

        self.setLayout(layout)

    def get_map_html(self):
        """HTML с OpenStreetMap для выбора координат."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Карта</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                html, body, #map {
                    height: 100%;
                    margin: 0;
                }
            </style>
            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([49.680414, 83.314745], 13); // Центр карты
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19
                }).addTo(map);

                map.on('click', function(e) {
                    var lat = e.latlng.lat;
                    var lng = e.latlng.lng;
                    console.log('Coordinates:', lat, lng);
                });
            </script>
        </body>
        </html>
        """

    def handle_js_console_message(self, level, message, line, source):
        """Обработка сообщений из консоли JavaScript."""
        if "Coordinates:" in message:
            try:
                coords = message.split(":")[1].strip().split(",")
                latitude, longitude = float(coords[0]), float(coords[1])
                self.coordinatesSelected.emit(latitude, longitude)
                self.close()
            except ValueError:
                pass
