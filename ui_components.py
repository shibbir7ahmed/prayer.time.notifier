from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QColor, QPainter, QFont, QCursor
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QLineEdit, QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QApplication, QSystemTrayIcon,QMessageBox
from prayer_time_handler import calculate_segments, determine_label_and_countdown, fetch_prayer_times
import datetime

class DraggableWindow(QWidget):
    def __init__(self, city_name, country_name, tray):
        super().__init__()
        try:
            # Initialize attributes
            self.city_name = city_name
            self.country_name = country_name
            self.tray = tray
            self.position_locked = False
            self.prayer_label = ""
            self.countdown_text = ""
            self.prayer_wakt = False  # Tracks whether the prayer wakt notification has been shown
            self.notified_30_minutes = False  # Tracks whether the 30-min reminder has been shown

            # Setup window properties
            self.setWindowTitle("City Display Window")
            # Set default position at the bottom-right corner of the screen
            screen_geometry = QApplication.desktop().screenGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Calculate position for bottom-right
            window_width = 300
            window_height = 50
            x_position = screen_width - window_width - 150  # 10px margin from right
            y_position = screen_height - window_height - 30  # 10px margin from bottom
            
            self.setGeometry(x_position, y_position, window_width, window_height)
            self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.setAttribute(Qt.WA_TranslucentBackground, True)

            # Create menu actions
            self.menu = QMenu(self)
            self.exit_action = QAction("Hide", self)
            self.lock_action = QAction("Lock Position", self)
            self.menu.addAction(self.exit_action)
            self.menu.addAction(self.lock_action)
            self.exit_action.triggered.connect(self.close)
            self.lock_action.triggered.connect(self.toggle_lock_position)

            self.update_lock_action()
            
            # Setup prayer times
            self.city_name = city_name
            self.country_name = country_name
            self.prayer_times = fetch_prayer_times(city_name, country_name)

            # Setup timers
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_prayer_info)
            self.timer.start(1000)  # Trigger update_prayer_info every second

            self.countdown_timer = QTimer(self)
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_timer.start(1000)

            # Fetch prayer times
            self.prayer_times = fetch_prayer_times(self.city_name, self.country_name)
            if not self.prayer_times:
                raise ValueError("Error fetching prayer times.")
            self.update_prayer_info()

            self.show()

        except ValueError as e:
            print(f"DraggableWindow initialization error: {e}")
            self.show_error_dialog("Initialization Error", f"An error occurred during initialization:\n{e}")
        except Exception as e:
            print(f"Unexpected DraggableWindow initialization error: {e}")
            self.show_error_dialog("Unexpected Error", f"An unexpected error occurred:\n{e}")

    def get_next_state(self, current_label):

        # Define the sequence of states
        states = ["FAJR", "Makruh1", "DUHA", "Makruh2", "ZUHR", "ASR", "Makruh3", "MAGHRIB", "ISHA", "Mid Night", "TAHAJJUT"]
    
        # Find the index of the current state
        current_index = states.index(current_label)
    
        # Determine the next state (wrap around to the beginning if at the end)
        next_index = (current_index + 1) % len(states)
        return states[next_index]

    def toggle_lock_position(self):
        self.position_locked = not self.position_locked
        self.update_lock_action()
        self.update()

    def update_lock_action(self):
        if self.position_locked:
            self.lock_action.setText("Unlock Position")
        else:
            self.lock_action.setText("Lock Position")

    def update_prayer_info(self):
        """Update prayer information with error handling."""
        try:
            if not self.prayer_times:
                self.prayer_label = "Error fetching prayer times"
                self.countdown_text = ""
                self.timer.start(60000)  # Retry in 1 minute
                self.update()  # Trigger UI update
                return
    
            # Calculate prayer time segments
            segments = calculate_segments(self.prayer_times)
            if not segments:
                self.prayer_label = "Error calculating prayer times"
                self.countdown_text = ""
                self.timer.start(60000)  # Retry in 1 minute
                self.update()  # Trigger UI update
                return
    
            # Determine the next prayer info
            prayer_info = determine_label_and_countdown(segments)
            self.prayer_label = prayer_info['label']
            next_time = prayer_info['next_time']
    
            if next_time and next_time > datetime.datetime.now():
                time_remaining = next_time - datetime.datetime.now()
                self.countdown_text = f"{time_remaining.seconds // 3600}h {(time_remaining.seconds // 60) % 60}m {time_remaining.seconds % 60}s"
                self.timer.start(max(1, int(time_remaining.total_seconds() * 1000)))
            else:
                self.prayer_label = "Prayer time error"
                self.countdown_text = ""
                self.timer.start(60000)  # Retry in 1 minute
    
        except Exception as e:
            print(f"Error in update_prayer_info: {e}")
            self.prayer_label = "Error updating prayer info"
            self.countdown_text = ""
            self.timer.start(60000)  # Retry in 1 minute
            self.update()  # Trigger UI update

    def update_countdown(self):
        try:
            # Validate prayer times
            if not self.prayer_times:
                self.countdown_text = "Prayer times unavailable"
                self.update()  # Trigger UI update
                return
    
            # Calculate segments
            segments = calculate_segments(self.prayer_times)
            if not segments:
                self.countdown_text = "Error calculating countdown"
                self.update()  # Trigger UI update
                return
    
            # Determine the next prayer time
            prayer_info = determine_label_and_countdown(segments)
            next_time = prayer_info.get('next_time')
            self.prayer_label = prayer_info.get('label', "UNKNOWN")  # Update class-level label
    
            if not next_time or next_time <= datetime.datetime.now():
                self.countdown_text = "Countdown unavailable"
                self.notified_30_minutes = False  # Reset 30-minute notification flag
                self.prayer_wakt = False  # Reset wakt notification flag
                self.update()  # Trigger UI update
                return
    
            # Calculate time remaining
            time_remaining = next_time - datetime.datetime.now()
    
            # Notify for 30-minute reminders
            if (
                0 < time_remaining.total_seconds() <= 1800 and
                not self.notified_30_minutes and
                self.prayer_label in ["FAJR", "ZUHR", "ASR", "MAGHRIB", "ISHA"]
            ):
                self.show_notification(
                    "Prayer Reminder",
                    f"Approx. 30 minutes left for {self.prayer_label}."
                )
                self.notified_30_minutes = True
    
            # Notify for wakt reminders
            if (
                 0 < time_remaining.total_seconds() <= 1 and  # Time has passed
                not self.prayer_wakt and  # Notification not already shown
                self.prayer_label in ["FAJR", "Makruh1", "DUHA", "Makruh2", "ZUHR", "ASR", "Makruh3", "MAGHRIB", "ISHA", "Mid Night", "TAHAJJUT"]
            ):
                next_state = self.get_next_state(self.prayer_label)
                
                self.show_notification(
                    "Prayer Reminder",
                    f"{next_state} Time Started!."
                )
                self.prayer_wakt = True  # Prevent repeated notifications
    
            # Update countdown text
            self.countdown_text = f"{time_remaining.seconds // 3600}h {(time_remaining.seconds // 60) % 60}m {time_remaining.seconds % 60}s"
            self.update()  # Trigger UI update
    
        except Exception as e:
            print(f"Error in update_countdown: {e}")
            self.countdown_text = "Error updating countdown"
            self.update()  # Trigger UI update

    def paintEvent(self, event):
        """Handle the painting of the window with error handling."""
        try:
            # Validate critical attributes
            if not self.city_name or not self.prayer_label or not self.countdown_text:
                raise ValueError("Missing critical data for rendering.")
    
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
    
            # Gradient Background with 90% Opacity
            background_color = QColor(248, 227, 33, int(255 * 1))  # F8E321 with 90% opacity
            painter.setBrush(background_color)
            painter.setPen(Qt.NoPen)

    
            # Font Setup
            font = QFont("Trebuchet MS", 14)
            painter.setFont(font)
    
            # Calculate Text Size
            text = f"{self.city_name} {self.prayer_label} left {self.countdown_text}"
            text_width = painter.fontMetrics().width(text)
            text_height = painter.fontMetrics().height()
    
            # Resize Window
            self.resize(text_width + 25, 32)
    
            # Draw Background
            painter.drawRoundedRect(0, 0, self.width() - 5, self.height() - 5, 10, 10)
    
            # Set Text Color (181B23) and Draw Text
            text_color = QColor("#181B23")  # Dark gray for text
            painter.setPen(text_color)
            x_pos = (self.width() - text_width) // 3
            y_pos = (self.height() + text_height) // 3
            painter.drawText(x_pos, y_pos, text)
    
        except ValueError as e:
            print(f"Paint error: {e}")
            self.show_error_dialog(
                "Rendering Error",
                f"An error occurred while rendering the window:\n{e}"
            )
        except Exception as e:
            print(f"Unexpected paint error: {e}")
            self.show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred during rendering:\n{e}"
            )

    def mousePressEvent(self, event):
        """Handle mouse press events with error handling."""
        try:
            if event.button() == Qt.RightButton:
                if not self.menu:
                    raise AttributeError("Context menu is not initialized.")
                self.menu.exec_(QCursor.pos())
            elif event.button() == Qt.LeftButton:
                self.offset = event.pos()
        except AttributeError as e:
            print(f"Mouse press error: {e}")
            self.show_error_dialog(
                "Context Menu Error",
                f"An error occurred while showing the context menu:\n{e}"
            )
        except Exception as e:
            print(f"Unexpected mouse press error: {e}")
            self.show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred during mouse press:\n{e}"
            )
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events with error handling."""
        try:
            if event.buttons() == Qt.LeftButton:
                if self.position_locked:
                    print("Position is locked; dragging is disabled.")
                    return
                if not self.offset:
                    raise ValueError("Offset is not initialized.")
                self.move(self.pos() + event.pos() - self.offset)
        except ValueError as e:
            print(f"Mouse move error: {e}")
            self.show_error_dialog(
                "Dragging Error",
                f"An error occurred while dragging the window:\n{e}"
            )
        except Exception as e:
            print(f"Unexpected mouse move error: {e}")
            self.show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred during dragging:\n{e}"
            )

    def show_notification(self, title, message):
        try:
            if self.tray and hasattr(self.tray, 'showMessage'):
                self.tray.showMessage(
                    title,
                    message,
                    QSystemTrayIcon.Information,
                    5000  # Notification duration in milliseconds
                )
            else:
                raise AttributeError("System tray is not initialized or does not support notifications.")
        except Exception as e:
            print(f"Error showing notification: {e}")



