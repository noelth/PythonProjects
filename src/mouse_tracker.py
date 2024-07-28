import sys
import math
import threading
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import QTimer, Qt
from pynput import mouse

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
        quit_action.triggered.connect(QApplication.instance().quit)

        self.menu.addAction(self.distance_action)
        self.menu.addAction(quit_action)

        # Set the context menu to the tray icon
        self.tray_icon.setContextMenu(self.menu)

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

    def handle_click(self, x, y, button, pressed):
        if pressed:
            print(f"Mouse button {button} pressed at ({x}, {y})")
            if button == mouse.Button.left:
                if self.menu.isVisible():
                    self.menu.hide()
                else:
                    print("Left button action outside context menu")
            elif button == mouse.Button.right:
                print("Right button action")
                self.show_menu(x, y)

    def show_menu(self, x, y):
        self.menu.exec_(QCursor.pos())

def start_mouse_listener(mouse_tracker):
    def on_click(x, y, button, pressed):
        mouse_tracker.handle_click(x, y, button, pressed)

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

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

    # Start the mouse listener in a separate thread
    listener_thread = threading.Thread(target=start_mouse_listener, args=(mouse_tracker,))
    listener_thread.daemon = True
    listener_thread.start()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()