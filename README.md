# Course Synchronization Automation

This project automates the process of synchronizing course memberships on the MEBIS learning platform. It allows users to manage course settings efficiently by selecting whether to synchronize members automatically.

## Features

- **Login Automation:** Automatically logs into the MEBIS platform using provided credentials.
- **Course ID Management:** Extracts course IDs from the user's courses or uses predefined course IDs from the configuration file.
- **Class Management:** Navigates through classes and updates synchronization settings.
- **CSV Logging:** Records processed course IDs to a CSV file to avoid reprocessing.
- **Configurable Settings:** Easily configure settings such as wait times and predefined course IDs through a configuration file.

## Requirements

- Python 3.x
- Selenium library
- Chrome WebDriver (ensure it matches your Chrome version)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/course-synchronization-automation.git
   cd course-synchronization-automation
   ```

2. Install the required Python packages:
    ```bash
    pip install selenium
    ```
3. Download the Chrome WebDriver that matches your Chrome version and ensure it's in your system's PATH.

4. Create a configuration file named config.ini in the project directory. Here’s a sample configuration:
```ini
    [login]
    username = your_username
    password = your_password

    [mode]
    headless = True  # or False, depending on your preference
    waittime = 5     # wait time in seconds

    [courses]
    course_ids = 1681687,1681688  # Comma-separated list of course IDs (optional)
```
# Usage
1. Run the script using Python:
```bash
python main.py
```
The script will log into the MEBIS platform, process the specified courses, and update the synchronization settings as configured.
Contributing
Contributions are welcome! If you have suggestions for improvements or want to report a bug, please open an issue or submit a pull request.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Acknowledgments
Thanks to the developers of Selenium for providing a powerful automation framework.
Thanks to the ByCS platform for enabling educational management through their system.
