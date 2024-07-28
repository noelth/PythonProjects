import sys
import math
#from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QWidget, QLabel, QVBoxLayout, QPushButton
#from PyQt5.QtGui import QIcon, QCursor
#from PyQt5.QtCore import QTimer, Qt

class MouseTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.total_distance = 0
        self.last_position = QCursor.pos()

        self.label = QLabel("Your mouse has travelled 0 km 0 m 0 cm 0 mm", self)
        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_stats)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.reset_button)
        self.setLayout(layout)

        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('Mouse Tracker')

        # Set window flags to make it frameless, always on top, and a tool window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Apply styles to make the window semi-transparent and match the dark UI theme
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);  /* Semi-transparent black background */
                color: white;
                border-radius: 10px;  /* Rounded corners */
            }
            QLabel {
                font-size: 18px;
                color: white;
            }
            QPushButton {
                background-color: rgba(50, 50, 50, 180);  /* Semi-transparent button background */
                color: white;
                border: 1px solid white;
                border-radius: 5px;  /* Rounded corners for the button */
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 180);  /* Darker button background on hover */
            }
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.track_mouse)
        self.timer.start(100)  # Track mouse every 100 milliseconds

    def track_mouse(self):
        current_position = QCursor.pos()
        dx = current_position.x() - self.last_position.x()
        dy = current_position.y() - self.last_position.y()
        distance = math.sqrt(dx * dx + dy * dy)

        # Convert screen pixels to centimeters (assuming 96 DPI)
        cm_per_pixel = 2.54 / 96
        distance_cm = distance * cm_per_pixel

        self.total_distance += distance_cm
        self.update_label()
        self.last_position = current_position

    def update_label(self):
        total_mm = int(self.total_distance * 10)  # Convert to millimeters
        km = total_mm // 1000000
        m = (total_mm // 1000) % 1000
        cm = (total_mm // 10) % 100
        mm = total_mm % 10
        self.label.setText(f"Your mouse has travelled {km} km {m} m {cm} cm {mm} mm")

    def reset_stats(self):
        self.total_distance = 0
        self.update_label()

def main():
    app = QApplication(sys.argv)

    # Hide the application from the dock and application switcher
    app.setQuitOnLastWindowClosed(False)

    # Use a standard PyQt5 icon for the system tray
    tray_icon = QSystemTrayIcon(QIcon(":/qt-project.org/styles/commonstyle/images/standardbutton-help-32.png"), app)
    tray_menu = QMenu()
    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(quit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    tracker = MouseTracker()

    def on_tray_icon_activated(reason):
        if reason == QSystemTrayIcon.Trigger:  # Left click
            if tracker.isVisible():
                tracker.hide()
            else:
                tracker.show()
                tracker.raise_()
                tracker.activateWindow()

    tray_icon.activated.connect(on_tray_icon_activated)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()