# prayer.time.notifier
Prayer Time Taskbar Application

Overview
The Prayer Time Taskbar Application is a lightweight Windows-based app designed to help Muslims track their daily prayer times. It is especially beneficial for individuals living in non-Muslim countries with limited access to mosques. The application integrates into the Windows system tray for quick and convenient access.
Features

    Prayer Times:
        Displays daily prayer times for Fajr, Dhuhr, Asr, Maghrib, and Isha.
        Includes additional times like Suhoor End (Imsak), Tahajjud, Sunrise, Sunset, and Makruh times.

    System Tray Integration:
        Provides quick access to prayer times, Hijri date, and other useful information.

    Notifications:
        Alerts 30 minutes before each prayer time.
        Notifies the user when a prayer time begins.

    Customizable Window:
        A draggable window that shows the next prayer time and countdown, with an option to lock its position.

    Hijri Date Display:
        Includes the current Hijri date in a user-friendly format.

    Safe Time Calculations:
        Adds buffer times around sunrise, sunset, and mid-noon to avoid forbidden prayer periods.

    Developer’s Note:
        Highlights the app's purpose and provides guidance for usage.

Installation

    Download and Install:
        Run the provided .exe installer file for Windows.

    Startup Integration:
        The app automatically adds itself to the Windows startup program, ensuring it runs when the computer boots.

    Launch the App:
        Once installed, the app resides in the system tray and runs silently in the background.

Opportunities for Future Development

    Cross-Platform Compatibility:
        Extend functionality to macOS and Linux.

    Localization:
        Add support for multiple languages to make it globally accessible.

    Customizable Features:
        Enable users to adjust notification settings, themes, and prayer calculation methods.

    Qibla Direction:
        Add a Qibla compass feature for convenience.

    Additional Features:
        Provide weather updates and prayer insights.

Contribution and Open Source

This application was developed with assistance from OpenAI's ChatGPT and is fully open-source.

    Editable and Upgradeable:
        The code is open for anyone to edit, upgrade, or adapt for their specific needs.
    Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.

Credits

    Built using Python and PyQt5 for GUI and system tray integration.
    Prayer times fetched via the Aladhan API.
