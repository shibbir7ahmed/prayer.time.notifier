from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QMessageBox

def show_notification(tray, title, message):
    try:
        tray.showMessage(
            title,
            message,
            QSystemTrayIcon.Information,
            5000  # Duration in milliseconds
        )
    except Exception as e:
        print(f"Error displaying notification: {e}")

def fallback_notification(title, message):
    try:
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Information)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()
    except Exception as e:
        print(f"Error displaying fallback notification: {e}")

# def notify_upcoming_prayer(tray, prayer_label):
#     show_notification(
#         tray,
#         "Prayer Reminder",
#         f"It's approximately 30 minutes left for {prayer_label}."
#     )

# def notify_wakt(tray, prayer_label):
#     show_notification(
#         tray,
#             "Prayer Reminder",
#             f"Starting {prayer_label} Time!."
        )
