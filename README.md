# WeatherGuard

**Project Link:** [https://github.com/skye-cyber/WeatherGuard](https://github.com/skye-cyber/WeatherGuard)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage](#usage)
6. [API Integration](#api-integration)
7. [Project Structure](#project-structure)
8. [Testing](#testing)
9. [Challenges & Key Learnings](#challenges--key-learnings)
10. [Future Enhancements](#future-enhancements)
11. [Contributing](#contributing)
12. [License](#license)
13. [Contact & Questions](#contact--questions)

---

## Introduction

**WeatherGuard** is a Django-based web application designed to provide real-time weather updates and send alerts when specific weather conditions are met (e.g., rain, storms, or extreme conditions). By integrating external RESTful services for weather data and notifications, WeatherGuard offers a modular and scalable solution for weather monitoring and alerting.

---

## Features

- **Real-Time Weather Updates:**  
  Retrieves current weather information based on user-defined locations.
  
- **Automated Alerts:**  
  Sends notifications (via email or SMS) when weather conditions trigger preset thresholds.
  
- **Modular Django Architecture:**  
  Separates concerns into distinct Django apps, enabling easy maintenance and scalability.
  
- **Responsive UI:**  
  Provides a user-friendly interface for displaying weather data and managing notification settings.
  
- **Configurable Settings:**  
  Users can adjust their default location and alert thresholds through the admin interface.

---

## System Architecture

WeatherGuard leverages Django’s robust framework to integrate multiple services into a single workflow:

      +---------------------------------+
      |         Django Frontend         |
      |  (Templates, Static Files, etc.)|
      +---------------+-----------------+
                      |
                      v
      +---------------+-----------------+
      |       Django Views & API        |
      | (Business Logic & Data Handling)|
      +---------------+-----------------+
                      |         \
                      |          \
                      v           v
     +----------------+--+     +---+-------------------+
     |  Weather Data API |     | Notification Service |
     |  (External REST)  |     |      (External REST) |
     +-------------------+     +----------------------+

- **Django Views/URLs:**  
  Serve both rendered pages and API endpoints to manage interactions.
  
- **External Services:**  
  - **Weather API:** Provides weather data via a RESTful call.
  - **Notification API:** Sends out notifications based on triggers.

---

## Installation & Setup

### Prerequisites

- **Python:** 3.8 or above
- **pip:** Python package installer
- **Virtual Environment Tool:** (e.g., `venv` or `virtualenv`)
- **Git:** For cloning the repository

### Clone the Repository

```bash
git clone https://github.com/skye-cyber/WeatherGuard.git
cd WeatherGuard
```
### Create and Activate a Virtual Environment
```bash
python -m venv venv
```
# On Windows:
```bash
venv\Scripts\activate
```
# On macOS/Linux:
```bash
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a .env file in the project root and add the following configuration:
```bash
# Django settings
DEBUG=True
SECRET_KEY=your_secret_key_here

# Weather API configuration
WEATHER_API_KEY=your_weather_api_key_here

# Notification API configuration
NOTIFICATION_API_KEY=your_notification_api_key_here
NOTIFICATION_SERVICE_URL=https://api.notificationservice.com/send

# Default location settings
DEFAULT_LOCATION=your_default_location
```

### Database Setup
Run migrations to set up the database:
```bash
python manage.py migrate
```

## Usage
### Running the Development Server
Start the Django development server with:

```bash
python manage.py runserver
```

Access the application at http://localhost:8000.

### Django Admin
Create a superuser to manage settings and view logs:
```bash
python manage.py createsuperuser
```
Then visit http://localhost:8000/admin and log in.

## API Integration
### Weather Data Endpoint
URL: /api/weather/?location={location}
Method: GET
#### Description:
Retrieves current weather information by forwarding a request to an external weather API.
Example Request:
```bash
curl "http://localhost:8000/api/weather/?location=Nairobi"
```
#### Response:
JSON data including temperature, humidity, weather conditions, etc.
#### Notification Trigger Endpoint
URL: /api/notify/
Method: POST
```Description:```
Checks weather data and sends a notification if certain criteria (e.g., rain forecast) are met.
Example Request Payload:

```bash
{
    "coord": {
        "lon": 36.8288,
        "lat": -1.3026
    },
    "weather": [
        {
            "id": 800,
            "main": "Clear",
            "description": "clear sky",
            "icon": "01d"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 300.39,
        "feels_like": 299.39,
        "temp_min": 300.39,
        "temp_max": 300.39,
        "pressure": 1010,
        "humidity": 20,
        "sea_level": 1010,
        "grnd_level": 840
    },
    "visibility": 10000,
    "wind": {
        "speed": 5.92,
        "deg": 83,
        "gust": 6.12
    },
    "clouds": {
        "all": 4
    },
}
```

#### Response:
JSON confirmation indicating the notification status.

## Project Structure
```bash
WeatherGuard/
├── weatherguard/            # Main Django project folder
│   ├── settings.py          # Django settings including .env integration
│   ├── urls.py              # URL declarations for the project
│   └── wsgi.py
├── apps/                    # Custom Django apps
│   ├── weather/             # Handles weather data retrieval and processing
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   └── notifications/       # Handles notification logic and integration
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── templates/
├── static/                  # Static files (CSS, JavaScript, images)
├── templates/               # Base HTML templates for the project
├── manage.py                # Django project management script
├── requirements.txt         # Python dependencies list
└── README.md                # Project documentation (this file)
```
## Testing
### Unit Tests:
Run tests with Django’s test framework:
```bash
python manage.py test
```

### Integration Tests:
Ensure all API endpoints interact correctly with external services.
### Manual Testing:
Validate functionality via the web interface and Django admin.

## Challenges & Key Learnings
### Challenges
1. ```External API Limitations:```
    Managing rate limits and ensuring reliable data fetching from external APIs.

    2. ```Asynchronous Processing:```
Coordinating asynchronous operations between fetching weather data and triggering notifications.

3. ```Secure Configuration Management:```
Keeping sensitive API keys and configuration secure while maintaining ease of development.

## Key Learnings
1. Service Composition in Django:
Decoupling weather data retrieval and notification logic into separate Django apps improves scalability.

2. Robust Error Handling:
Implementing comprehensive error handling ensures better resilience against external API failures.

3. User Experience:
A clean, responsive UI backed by Django’s templating system leads to improved usability.

## Future Enhancements
1. Multi-Channel Notifications:
Extend support to include SMS, push notifications, and more.

2. User Customization:
Allow users to set personalized weather thresholds and alert preferences.

3. Data Analytics:
Integrate historical weather data and predictive analytics.
Performance Improvements:
Optimize caching and reduce API call latency.

## Contributing
Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:
```bash
git checkout -b feature/YourFeature
```
Make your changes and commit
```bash
git commit -m 'Add new feature'
```
Push to your branch:
```bash
git push origin feature/YourFeature
```
Open a Pull Request with a detailed description of your changes.


## License
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
  See the LICENSE file for more details. See the [LICENSE](LICENSE) file for details.

## Contact & Questions
For any questions, clarifications, or suggestions, please feel free to:

Open an issue in this repository.
Contact the maintainer via email: skye.cyber@example.com
Visit our GitHub profile: skye-cyber
