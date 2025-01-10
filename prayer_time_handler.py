import requests
import datetime
import time
from PyQt5.QtWidgets import QMessageBox

def fetch_prayer_times(city_name, country_name):
    """Fetch prayer times using the city and country."""
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city_name}&country={country_name}&method=2"
    print(f"Fetching prayer times from: {url}")

    while True:  # Retry loop
        try:
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                print(f"API returned status code {response.status_code}")
                raise requests.RequestException(f"API Error: {response.status_code}")

            data = response.json()
            if "data" in data and "timings" in data["data"]:
                print("Successfully fetched prayer times!")
                return data["data"]["timings"]
            else:
                raise ValueError("Unexpected API response format.")

        except requests.RequestException as e:
            print(f"Network error occurred: {e}. Retrying in 5 seconds...")
        except ValueError as e:
            print(f"Parsing error: {e}. Retrying in 5 seconds...")
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")

        time.sleep(5)


# def fetch_prayer_times(city_name, country_name):
#     """Mock prayer times for testing."""
#     print("Debug: Using mock prayer times.")
#     return {
#         "Fajr": "05:00",
#         "Sunrise": "06:30",
#         "Dhuhr": "12:00",
#         "Asr": "15:30",
#         "Maghrib": "17:45",
#         "Isha": "21:49",
#         "Midnight": "23:46"
#     }

def show_error_dialog(title, message):
    """Display an error dialog to the user."""
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Warning)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()

def calculate_segments(prayer_times):
    """Calculate prayer time segments with error handling for invalid data."""
    if not prayer_times:
        show_error_dialog(
            "Prayer Times Error", 
            "Prayer times data is missing or invalid. Please check your internet connection or input."
        )
        return None  # Return None to indicate an error
    
    try:
        now = datetime.datetime.now()
        today_date = datetime.datetime(now.year, now.month, now.day)

        def get_time_from_prayer_string(prayer_time_string):
            hours, minutes = map(int, prayer_time_string.split(':'))
            return today_date + datetime.timedelta(hours=hours, minutes=minutes)

        # Extract and parse prayer times
        fajr_time = get_time_from_prayer_string(prayer_times.get('Fajr', '00:00'))
        sunrise_time = get_time_from_prayer_string(prayer_times.get('Sunrise', '00:00'))
        dhuhr_time = get_time_from_prayer_string(prayer_times.get('Dhuhr', '00:00'))
        asr_time = get_time_from_prayer_string(prayer_times.get('Asr', '00:00'))
        maghrib_time = get_time_from_prayer_string(prayer_times.get('Maghrib', '00:00'))
        isha_time = get_time_from_prayer_string(prayer_times.get('Isha', '00:00'))
        # midnight_time = get_time_from_prayer_string(prayer_times.get('Midnight', '00:00'))
        # Calculate Midnight mathematically
        time_difference = fajr_time - maghrib_time
        if time_difference.days < 0:  # Handle overnight time crossing
            time_difference += datetime.timedelta(days=1)

        midnight_time = maghrib_time + (time_difference / 2)
        lastthird_time = get_time_from_prayer_string(prayer_times.get('Lastthird', '00:00')) + datetime.timedelta(days=1)
        next_fajr_time = fajr_time + datetime.timedelta(days=1)
        haram1_end = sunrise_time + datetime.timedelta(minutes=10)
        haram2_start = dhuhr_time - datetime.timedelta(minutes=5)
        haram3_start = maghrib_time - datetime.timedelta(minutes=10)

        return {
            "fajr_time": fajr_time,
            "sunrise_time": sunrise_time,
            "haram1_end": haram1_end,
            "dhuhr_time": dhuhr_time,
            "haram2_start": haram2_start,
            "asr_time": asr_time,
            "haram3_start": haram3_start,
            "maghrib_time": maghrib_time,
            "isha_time": isha_time,
            "midnight_time": midnight_time,
            "lastthird_time": lastthird_time,
            "next_fajr_time": next_fajr_time
        }
    except ValueError as e:
        show_error_dialog(
            "Prayer Times Parsing Error", 
            f"An error occurred while processing prayer times:\n{e}"
        )
        return None
    except Exception as e:
        show_error_dialog(
            "Unexpected Error", 
            f"An unexpected error occurred during prayer times calculation:\n{e}"
        )
        return None

def determine_label_and_countdown(segments):
    if not segments:
        # If no segments, return UNKNOWN and notify the user via error dialog
        show_error_dialog(
            "Prayer Time Segments Error",
            "Prayer time segments are missing or invalid. Please check your settings or internet connection."
        )
        return {'next_time': None, 'label': 'UNKNOWN'}

    try:
        now = datetime.datetime.now()

        # Evaluate the current time against prayer segments and determine the label
        if now >= segments.get('fajr_time', now) and now < segments.get('sunrise_time', now):
            return {'next_time': segments['sunrise_time'], 'label': 'FAJR'}
        elif now >= segments.get('sunrise_time', now) and now < segments.get('haram1_end', now):
            return {'next_time': segments['haram1_end'], 'label': 'Makruh1'}
        elif now >= segments.get('haram1_end', now) and now < segments.get('haram2_start', now):
            return {'next_time': segments['haram2_start'], 'label': 'DUHA'}
        elif now >= segments.get('haram2_start', now) and now < segments.get('dhuhr_time', now):
            return {'next_time': segments['dhuhr_time'], 'label': 'Makruh2'}
        elif now >= segments.get('dhuhr_time', now) and now < segments.get('asr_time', now):
            return {'next_time': segments['asr_time'], 'label': 'ZUHR'}
        elif now >= segments.get('asr_time', now) and now < segments.get('haram3_start', now):
            return {'next_time': segments['haram3_start'], 'label': 'ASR'}
        elif now >= segments.get('haram3_start', now) and now < segments.get('maghrib_time', now):
            return {'next_time': segments['maghrib_time'], 'label': 'Makruh3'}
        elif now >= segments.get('maghrib_time', now) and now < segments.get('isha_time', now):
            return {'next_time': segments['isha_time'], 'label': 'MAGHRIB'}
        elif now >= segments.get('isha_time', now) and now < segments.get('midnight_time', now):
            return {'next_time': segments['midnight_time'], 'label': 'ISHA'}
        elif now >= segments.get('midnight_time', now) and now < segments.get('lastthird_time', now):
            return {'next_time': segments['lastthird_time'], 'label': 'Mid Night'}
        elif now >= segments.get('lastthird_time', now) and now < segments.get('next_fajr_time', now):
            return {'next_time': segments['next_fajr_time'], 'label': 'TAHAJJUT'}
        else:
            # Default to the next Fajr if no other case matches
            return {'next_time': segments.get('fajr_time', now), 'label': 'TAHAJJUT'}

    except KeyError as e:
        # Handle missing keys gracefully
        show_error_dialog(
            "Segment Data Error",
            f"Key error while accessing segment data:\n{e}"
        )
        return {'next_time': None, 'label': 'UNKNOWN'}
    except Exception as e:
        # Handle unexpected errors
        show_error_dialog(
            "Unexpected Error",
            f"An unexpected error occurred during countdown determination:\n{e}"
        )
        return {'next_time': None, 'label': 'UNKNOWN'}


# if __name__ == "__main__":
#     # Test prayer times fetch functionality
#     city_name = "Makkah"
#     country_name = "Saudi Arabia"

#     print(f"Fetching prayer times for {city_name}, {country_name}...")
#     prayer_times = fetch_prayer_times(city_name, country_name)

#     if prayer_times:
#         print("Prayer times fetched successfully!")
#         print(prayer_times)

#         print("\nCalculating prayer segments...")
#         segments = calculate_segments(prayer_times)
#         print(segments)

#         print("\nDetermining the next prayer time...")
#         prayer_info = determine_label_and_countdown(segments)
#         print(prayer_info)
#     else:
#         print("Failed to fetch prayer times.")
