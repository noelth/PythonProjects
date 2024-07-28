import sys
import os
import math
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor, QScreen
from PyQt5.QtCore import QTimer, Qt, QPoint

class MouseTracker:
    def __init__(self, tray_icon):
        self.total_distance = 0
        self.last_position = QCursor.pos()
        self.tray_icon = tray_icon
        self.initUI()

    def initUI(self):
        # Create the context menu and actions
        self.menu = QMenu()
        self.distance_action = QAction("Mouse travel: 0 km 0 m 0 cm 0 mm", self.menu)
        self.distance_action.triggered.connect(self.reset_stats)
        
        quit_action = QAction("Quit", self.menu)
        quit_action.triggered.connect(self.quit_app)  # Connect to quit_app method

        self.menu.addAction(self.distance_action)
        self.menu.addAction(quit_action)

        # Remove or comment out the following line to prevent automatic context menu on right-click
        # self.tray_icon.setContextMenu(self.menu)

        # Connect the activated signal to the handle_tray_icon_click method
        self.tray_icon.activated.connect(self.handle_tray_icon_click)

        # Start a timer to update the distance
        self.timer = QTimer()
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
        self.distance_action.setText(f"Mouse travel: {km} km {m} m {cm} cm {mm} mm")

    def reset_stats(self):
        self.total_distance = 0
        self.update_label()
        self.menu.hide()  # Ensure the menu is hidden after resetting
        QTimer.singleShot(0, self.show_menu)  # Show the menu again if needed

    def handle_tray_icon_click(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Left-click
            if self.menu.isVisible():
                QTimer.singleShot(0, self.menu.hide)
                print("Menu closed")  # Added comment to indicate menu closed
            else:
                QTimer.singleShot(0, self.show_menu)

    def show_menu(self):
        # Calculate the position to show the menu
        icon_geometry = self.tray_icon.geometry()
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        menu_x = icon_geometry.left()
        menu_y = icon_geometry.bottom()

        # Adjust the position to align with the bottom-left corner of the tray icon
        self.menu.move(QPoint(menu_x, menu_y))
        self.menu.exec_(self.menu.pos())

    def quit_app(self):
        print("Quitting application")
        self.tray_icon.hide()  # Hide the tray icon before quitting
        QApplication.quit()  # Ensures the application quits immediately
        os._exit(0)  # Forcefully terminate the Python process

def main():
    app = QApplication(sys.argv)

    # Hide the application from the dock and application switcher
    app.setQuitOnLastWindowClosed(False)

    # Load the tray icon
    icon_path = ":/qt-project.org/styles/commonstyle/images/standardbutton-help-32.png"
    icon = QIcon(icon_path)

    tray_icon = QSystemTrayIcon(icon, app)
    mouse_tracker = MouseTracker(tray_icon)

    tray_icon.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()