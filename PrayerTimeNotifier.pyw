import sys
from PyQt5.QtWidgets import QApplication, QDialog, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from ui_components import DraggableWindow
from input_dialog import CityCountryInputDialog  # Import the input dialog from the new file
from taskbar_tray import SystemTray


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        # Create a dialog for city and country input
        dialog = CityCountryInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            city_name, country_name = dialog.get_city_country()

            if not city_name or not country_name:
                print("City or country name was not provided. Exiting.")
                sys.exit(1)

            # Create the draggable window
            window = DraggableWindow(city_name, country_name, None)

            # Create the system tray icon and link the window
            tray = SystemTray(app, window)
            window.tray = tray  # Link the tray to the window
            tray.setIcon(QIcon("icon.png"))
            tray.show()  # Show the tray icon

            # Prevent app exit on window close
            app.lastWindowClosed.connect(lambda: app.setQuitOnLastWindowClosed(False))

            sys.exit(app.exec_())
        else:
            print("Dialog was canceled.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
