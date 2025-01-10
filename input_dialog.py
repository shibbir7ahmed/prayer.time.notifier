from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QLabel, QDialogButtonBox, QMessageBox, QCompleter,QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import requests


class CityCountryInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("Prayer Time App")
            self.setFixedSize(300, 120)  # Keep dialog box size constant

            # Set the icon for the dialog
            self.setWindowIcon(QIcon("icon.png"))  # Use "icon.png" or "icon.ico" in the working directory

            # Fetch city and country list
            self.city_country_list = self.fetch_city_country_data()

            layout = QVBoxLayout()

            # Label for the city input with customizable font size
            self.city_label = QLabel("Your City Name:")
            self.city_label.setAlignment(Qt.AlignCenter)
            self.city_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;      /* Change the font size here */
                    font-weight: bold;    /* Optional: Make the font bold */
                    padding-top: 1px;    /* Add top padding */
                    padding-bottom: 5px; /* Add bottom padding */
                }
            """)
            layout.addWidget(self.city_label)

            # Add additional instruction line
            self.loading_note = QLabel("(please wait some moments for loading)")
            self.loading_note.setAlignment(Qt.AlignCenter)
            self.loading_note.setStyleSheet("font-size: 12px; color: gray;")
            layout.addWidget(self.loading_note)

            # Input box for city with updated typing space
            self.city_input = QLineEdit(self)
            self.city_input.setPlaceholderText("Type your city...")
            self.city_input.setStyleSheet("""
                QLineEdit {
                    font-size: 12px;  /* Change the font size here */
                    padding-left: 10px;  /* Add left padding for better typing space */
                    padding-right: 10px; /* Add right padding for better typing space */
                    height: 30px;  /* Adjust height if necessary */
                    
                }
            """)
            layout.addWidget(self.city_input)


            # Autocomplete functionality for the input box
            completer = QCompleter(self.city_country_list, self)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.city_input.setCompleter(completer)

            # Dialog buttons
            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
            self.button_box.accepted.connect(self.validate_and_accept)
            self.button_box.rejected.connect(self.reject)
            layout.addWidget(self.button_box)

            self.setLayout(layout)

        except Exception as e:
            print(f"Error initializing CityCountryInputDialog: {e}")


    def fetch_city_country_data(self):
        """
        Fetch a list of cities and countries from the API.
        """
        try:
            url = "https://countriesnow.space/api/v0.1/countries"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to fetch city and country data.")

            data = response.json()
            city_country_list = []
            for country in data['data']:
                country_name = country['country']
                cities = country.get('cities', [])
                for city in cities:
                    city_country_list.append(f"{city}, {country_name}")

            return city_country_list
        except Exception as e:
            print(f"Error fetching city and country data: {e}")
            return []

    def validate_and_accept(self):
        """
        Validate if the input matches the city-country list and accept the dialog.
        """
        user_input = self.city_input.text().strip()
        if user_input not in self.city_country_list:
            QMessageBox.warning(self, "Input Error", "Please select a city from the list.")
            return

        # Parse selected city and country
        if ", " in user_input:
            self.selected_city, self.selected_country = user_input.split(", ", 1)
        else:
            self.selected_city = user_input
            self.selected_country = ""

        self.accept()

    def get_city_country(self):
        """
        Return the selected city and country.
        """
        if not self.selected_city:
            QMessageBox.warning(self, "Input Error", "Please select a valid city.")
            return None, None
        return self.selected_city, self.selected_country
