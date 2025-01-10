from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QDialog, QLabel, QVBoxLayout,QMessageBox
from PyQt5.QtGui import QIcon,QPixmap
import requests
import datetime
from prayer_time_handler import calculate_segments

class SystemTray(QSystemTrayIcon):
    def __init__(self, app, window):
        super().__init__()
        self.window = window
        self.app = app

        try:
            # Set the icon for the tray
            icon_path = "icon.png"
            if not QPixmap(icon_path).isNull():
                self.setIcon(QIcon(icon_path))
            else:
                raise FileNotFoundError(f"Icon file not found: {icon_path}")

            # Create the context menu for the tray
            self.tray_menu = QMenu()

            # Add submenus and options in the desired order
            self.prayer_times_menu = QMenu("Today's Prayers", self.tray_menu)
            self.tray_menu.addMenu(self.prayer_times_menu)
            
            self.tahajjud_menu = QMenu("Tahajjud", self.tray_menu)
            self.tray_menu.addMenu(self.tahajjud_menu)
            
            self.imsak_menu = QMenu("Suhoor End", self.tray_menu)
            self.tray_menu.addMenu(self.imsak_menu)
            
            self.sunrise_sunset_menu = QMenu("Sunrise/Sunset", self.tray_menu)
            self.tray_menu.addMenu(self.sunrise_sunset_menu)
            
            # Add the Makruh Times submenu immediately after Sunrise/Sunset
            self.makruh_menu = QMenu("Makruh Times", self.tray_menu)
            self.tray_menu.addMenu(self.makruh_menu)
            
            self.hijri_date_menu = QMenu("Hijri Date", self.tray_menu)
            self.tray_menu.addMenu(self.hijri_date_menu)

            # Add lock, note, and exit actions
            self.lock_position_action = QAction("Lock Position", self)
            self.lock_position_action.triggered.connect(self.toggle_lock_position)
            self.tray_menu.addAction(self.lock_position_action)
            
            note_action = QAction("Note", self)
            note_action.triggered.connect(self.show_note_dialog)
            self.tray_menu.addAction(note_action)
            
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.exit_application)
            self.tray_menu.addAction(exit_action)

            # Set the menu
            self.setContextMenu(self.tray_menu)

            # Connect tray icon click signal
            self.activated.connect(self.icon_activated)

            # Initialize prayer times menus
            self.update_prayer_times_menu()

        except FileNotFoundError as e:
            self.show_error_dialog("Tray Icon Error", str(e))
            self.setIcon(QIcon())  # Use a blank icon as a fallback
        except Exception as e:
            self.show_error_dialog("Tray Initialization Error", f"An error occurred during tray initialization:\n{e}")

    def show_error_dialog(self, title, message):
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()

    def show_note_dialog(self):
        try:
            print("Opening Note dialog")  # Debug
            dialog = QDialog()
            dialog.setWindowTitle("Important Notice")
            dialog.setModal(True)  # Ensure it's modal
    
            layout = QVBoxLayout()
            message_label = QLabel(
                "<div style='text-align: center;'>"
                "<b><span style='font-size: 13px;'>Important Notice:</span></b><br>"
                "</div>"
                "<p style='font-size: 12px;'>This application is designed specifically for Muslims living in non-Muslim countries where access to mosques is limited.</p>"
                "<p style='font-size: 12px;'>"
                "<b>• Prayer Times Source:</b>"
                " The app retrieves prayer times from <i>www.aladhan.com</i> based on the city and country you provide. The ASR start time is earlier, because the app displays the Maliki/Shafi/Hanbli method."
                "</p>"
                "<p style='font-size: 12px;'>"
                "<b>• Safety Calculations:</b>"
                " For safety, the app accounts for-<br>"
                "&#8226; 10 minutes of forbidden time after sunrise and before sunset.<br>"
                "&#8226; 5 minutes of forbidden time around mid-noon."
                "</p>"
                "<p style='font-size: 12px;'>"
                "<b>• Tahajjut Calculation:</b>"
                " According to hadith, the best time of tahajjut is the last third of the night. The app calculates the last third time from Maghrib to next day Fajr."
                "</p>"
                "<p style='font-size: 12px;'>"
                "<b>• Ramadan Guidance:</b>"
                " During Ramadan, it is recommended to follow your local Imam’s timings for suhoor and breaking fast, as they may consider specific community practices."
                "</p>"
                "<div style='text-align: center;'>"
                "<p style='font-size: 12px;'>In-Sha-Allah this app serves as a helpful companion for your daily prayers.</p>"
                "</div>"
            )
            message_label.setWordWrap(True)
            message_label.setAlignment(Qt.AlignLeft)
            layout.addWidget(message_label)
            dialog.setLayout(layout)
            dialog.adjustSize()
            dialog.exec_()
            print("Note dialog closed")  # Debug
    
        except Exception as e:
            self.show_error_dialog("Note Dialog Error", f"An error occurred while displaying the note dialog:\n{e}")

    def clear_menus(self):
        """Clear all submenus to reset them."""
        try:
            self.prayer_times_menu.clear()
            self.imsak_menu.clear()
            self.tahajjud_menu.clear()
            self.sunrise_sunset_menu.clear()
            self.hijri_date_menu.clear()
        except Exception as e:
            print(f"Error clearing menus: {e}")

    def show_fallback_menus(self, message="Error updating menu"):
        """Populate submenus with fallback messages."""
        try:
            self.prayer_times_menu.clear()
            self.prayer_times_menu.addAction(message)

            self.imsak_menu.clear()
            self.imsak_menu.addAction("Error fetching Imsak time")

            self.tahajjud_menu.clear()
            self.tahajjud_menu.addAction("Error calculating Tahajjud time")

            self.sunrise_sunset_menu.clear()
            self.sunrise_sunset_menu.addAction("Error fetching Sunrise/Sunset times")

            self.hijri_date_menu.clear()
            self.hijri_date_menu.addAction("Error fetching Hijri date")
        except Exception as e:
            print(f"Error displaying fallback menus: {e}")
            
    def update_prayer_times_menu(self):
            """Update all submenus with the latest prayer times and related information."""
            if self.window.prayer_times:
                prayer_times = self.window.prayer_times
                segments = calculate_segments(prayer_times)
    
                # Update Prayer Times submenu
                self.prayer_times_menu.clear()
                self.prayer_times_menu.addAction(f"Fajr: {segments['fajr_time'].strftime('%I:%M %p')}")
                self.prayer_times_menu.addAction(f"Duha: {(segments['sunrise_time'] + datetime.timedelta(minutes=20)).strftime('%I:%M %p')}")
                self.prayer_times_menu.addAction(f"Zuhr: {segments['dhuhr_time'].strftime('%I:%M %p')}")
                self.prayer_times_menu.addAction(f"Asr: {segments['asr_time'].strftime('%I:%M %p')}")
                self.prayer_times_menu.addAction(f"Maghrib: {segments['maghrib_time'].strftime('%I:%M %p')}")
                self.prayer_times_menu.addAction(f"Esha: {segments['isha_time'].strftime('%I:%M %p')}")
    
                # Update Imsak submenu
                self.imsak_menu.clear()
                imsak_time = prayer_times.get('Imsak', 'N/A')
                if imsak_time != 'N/A':
                    imsak_datetime = datetime.datetime.strptime(imsak_time, "%H:%M").strftime("%I:%M %p")
                    self.imsak_menu.addAction(f"Imsak: {imsak_datetime}")
                else:
                    self.imsak_menu.addAction("Error fetching Imsak time")
    
                # Update Tahajjud submenu
                self.tahajjud_menu.clear()
                if "lastthird_time" in segments and "fajr_time" in segments:
                    self.tahajjud_menu.addAction(
                        f"Appr. Best Time: {segments['lastthird_time'].strftime('%I:%M %p')} - {segments['fajr_time'].strftime('%I:%M %p')}"
                    )
                else:
                    self.tahajjud_menu.addAction("Error calculating Tahajjud time")
    
                # Update Makruh Times submenu
                self.makruh_menu.clear()
                self.makruh_menu.addAction(
                    f"After Fajr: {segments['fajr_time'].strftime('%I:%M %p')} - {segments['sunrise_time'].strftime('%I:%M %p')}"
                )
                self.makruh_menu.addAction(
                    f"Before Zuhr: {(segments['dhuhr_time'] - datetime.timedelta(minutes=5)).strftime('%I:%M %p')} - {segments['dhuhr_time'].strftime('%I:%M %p')}"
                )
                self.makruh_menu.addAction(
                    f"Before Maghrib: {(segments['maghrib_time'] - datetime.timedelta(minutes=15)).strftime('%I:%M %p')} - {segments['maghrib_time'].strftime('%I:%M %p')}"
                )
    
                # Update Sunrise/Sunset submenu
                self.sunrise_sunset_menu.clear()
                self.sunrise_sunset_menu.addAction(f"Sunrise: {segments['sunrise_time'].strftime('%I:%M %p')}")
                self.sunrise_sunset_menu.addAction(f"Sunset: {segments['maghrib_time'].strftime('%I:%M %p')}")
    
                # Update Hijri Date submenu
                self.hijri_date_menu.clear()
                hijri_date = self.get_hijri_date()
                if hijri_date:
                    self.hijri_date_menu.addAction(hijri_date)
                else:
                    self.hijri_date_menu.addAction("Error fetching Hijri date")
                    
    def get_hijri_date(self):
        """Fetch the Hijri date from the API."""
        try:
            response = requests.get("https://api.aladhan.com/v1/gToH", timeout=5)
            if response.status_code == 200:
                data = response.json()
                hijri_data = data['data']['hijri']
                day = hijri_data['day']
                month = hijri_data['month']['en']  # English month name
                year = hijri_data['year']
                formatted_hijri_date = f"{day.zfill(2)} {month} {year}"  # e.g., 09 Jumādá al-ākhirah 1446
                return formatted_hijri_date
            else:
                print(f"Error fetching Hijri date: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"Error fetching Hijri date: {e}")
            return None
    def toggle_lock_position(self):
        """Toggle lock position on the window with error handling."""
        try:
            if not hasattr(self.window, 'toggle_lock_position'):
                raise AttributeError("Window does not have a 'toggle_lock_position' method.")
            
            self.window.toggle_lock_position()  # Calls the method in DraggableWindow to toggle position lock
            self.update_lock_position_action_text()
        except AttributeError as e:
            self.show_error_dialog(
                "Lock Position Error",
                f"An error occurred while toggling the lock position:\n{e}"
            )
        except Exception as e:
            self.show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred:\n{e}"
            )

    def update_lock_position_action_text(self):
        """Update the lock position action text."""
        if self.window.position_locked:
            self.lock_position_action.setText("Unlock Position")
        else:
            self.lock_position_action.setText("Lock Position")

    def exit_application(self):
        """Close the window and quit the application with error handling."""
        try:
            # Safely stop timers if they exist
            if hasattr(self.window, 'timer') and self.window.timer.isActive():
                self.window.timer.stop()
            if hasattr(self.window, 'countdown_timer') and self.window.countdown_timer.isActive():
                self.window.countdown_timer.stop()
    
            # Close the main window if it exists
            if hasattr(self.window, 'close'):
                self.window.close()
    
            # Quit the application
            self.app.quit()
    
        except Exception as e:
            self.show_error_dialog(
                "Exit Error",
                f"An error occurred while exiting the application:\n{e}"
            )

    def icon_activated(self, reason):
        """Handle the tray icon click to toggle between minimize and maximize with error handling."""
        try:
            if reason == QSystemTrayIcon.Trigger:
                if not hasattr(self.window, 'isVisible'):
                    raise AttributeError("Window does not support visibility toggling.")
                
                if self.window.isVisible():
                    self.window.hide()
                else:
                    self.window.showNormal()  # Show the window in normal size (not minimized)
        except AttributeError as e:
            self.show_error_dialog(
                "Visibility Toggle Error",
                f"An error occurred while toggling window visibility:\n{e}"
            )
        except Exception as e:
            self.show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred:\n{e}"
            )
