document.getElementById('settings-button').addEventListener('click', () => {
    document.getElementById('settings-modal').classList.remove('hidden');
});

document.getElementById('auto-detect-button').addEventListener('click', async () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            const apiKey = 'YOUR_API_KEY';
            const url = `http://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`;
            const response = await fetch(url);
            const data = await response.json();
            document.getElementById('location-input').value = data.name;
            updateLocationDisplay(data.name);
            fetchWeather(data.name);
        });
    } else {
        alert('Geolocation is not supported by this browser.');
    }
});

document.getElementById('save-settings').addEventListener('click', () => {
    const settings = {
        location: document.getElementById('location-input').value,
        username: document.getElementById('username-input').value,
        phone: document.getElementById('phone-input').value,
        email: document.getElementById('email-input').value,
        smsNotification: document.getElementById('sms-notification').checked,
        emailNotification: document.getElementById('email-notification').checked,
        hourlyNotification: document.getElementById('hourly-notification').checked,
        dailyNotification: document.getElementById('daily-notification').checked,
        weeklyNotification: document.getElementById('weekly-notification').checked,
        verbosity: document.querySelector('input[name="verbosity"]:checked').value
    };

    localStorage.setItem('settings', JSON.stringify(settings));
    document.getElementById('settings-modal').classList.add('hidden');

    if (settings.location) {
        updateLocationDisplay(settings.location);
        fetchWeather(settings.location);
    }
});

document.getElementById('toggle-theme').addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
});

document.getElementById('edit-location').addEventListener('click', () => {
    const locationValue = document.getElementById('location-value').innerText;
    document.getElementById('location-input').value = locationValue;
    document.getElementById('location-display').classList.add('hidden');
    document.getElementById('location-edit').classList.remove('hidden');
});

document.getElementById('save-location').addEventListener('click', () => {
    const locationValue = document.getElementById('location-input').value;
    updateLocationDisplay(locationValue);
    document.getElementById('location-display').classList.remove('hidden');
    document.getElementById('location-edit').classList.add('hidden');
    fetchWeather(locationValue);
});

document.getElementById('cancel-edit').addEventListener('click', () => {
    document.getElementById('location-display').classList.remove('hidden');
    document.getElementById('location-edit').classList.add('hidden');
});

function updateLocationDisplay(location) {
    document.getElementById('location-value').innerText = location;
    const settings = JSON.parse(localStorage.getItem('settings')) || {};
    settings.location = location;
    localStorage.setItem('settings', JSON.stringify(settings));
}

document.addEventListener('DOMContentLoaded', () => {
    const settings = JSON.parse(localStorage.getItem('settings')) || {};

    if (settings.location) {
        updateLocationDisplay(settings.location);
        fetchWeather(settings.location);
    } else {
        document.getElementById('no-weather').classList.remove('hidden');
        document.getElementById('current-weather').classList.add('hidden');
    }

    if (settings.username) {
        document.getElementById('username-input').value = settings.username;
    }

    if (settings.phone) {
        document.getElementById('phone-input').value = settings.phone;
    }

    if (settings.email) {
        document.getElementById('email-input').value = settings.email;
    }

    if (settings.smsNotification) {
        document.getElementById('sms-notification').checked = true;
    }

    if (settings.emailNotification) {
        document.getElementById('email-notification').checked = true;
    }

    if (settings.hourlyNotification) {
        document.getElementById('hourly-notification').checked = true;
    }

    if (settings.dailyNotification) {
        document.getElementById('daily-notification').checked = true;
    }

    if (settings.weeklyNotification) {
        document.getElementById('weekly-notification').checked = true;
    }

    if (settings.verbosity) {
        document.querySelector(`input[name="verbosity"][value="${settings.verbosity}"]`).checked = true;
    }

    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
    }
});

async function fetchWeather(city) {
    const apiKey = 'YOUR_API_KEY';
    const url = `http://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;
    const response = await fetch(url);
    const data = await response.json();
    displayWeather(data);
    fetchWeeklyForecast(city);
}

function displayWeather(weatherData) {
    document.getElementById('no-weather').classList.add('hidden');
    document.getElementById('current-weather').classList.remove('hidden');

    document.getElementById('current-temperature').innerText = `${weatherData.main.temp} °C`;
    document.getElementById('current-description').innerText = weatherData.weather[0].description;
    document.getElementById('current-icon').src = `http://openweathermap.org/img/wn/${weatherData.weather[0].icon}.png`;
}

async function fetchWeeklyForecast(city) {
    const apiKey = 'YOUR_API_KEY';
    const url = `http://api.openweathermap.org/data/2.5/forecast?q=${city}&appid=${apiKey}&units=metric`;
    const response = await fetch(url);
    const data = await response.json();
    displayWeeklyForecast(data);
}

function displayWeeklyForecast(forecastData) {
    const weeklyForecastElement = document.getElementById('weekly-forecast');
    weeklyForecastElement.innerHTML = '';

    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const currentDate = new Date();
    const currentDayIndex = currentDate.getDay();

    const groupedForecast = groupForecastByDay(forecastData.list);

    Object.keys(groupedForecast).forEach((day, index) => {
        const date = new Date(currentDate);
        date.setDate(currentDate.getDate() + index);
        const dayName = days[day];

        const forecastCard = document.createElement('div');
        forecastCard.classList.add('forecast-card', 'p-4', 'bg-white', 'dark:bg-gray-800', 'rounded-lg', 'shadow-md', 'flex-1', 'max-w-sm', 'mb-4');

        forecastCard.innerHTML = `
            <p class="date font-bold">${dayName}, ${date.toLocaleDateString()}</p>
            <img class="weather-icon w-10 h-10" src="http://openweathermap.org/img/wn/${groupedForecast[day][0].weather[0].icon}.png" alt="Weather Icon">
            <p class="temperature text-xl">${Math.round(groupedForecast[day][0].main.temp)} °C</p>
            <p class="description">${groupedForecast[day][0].weather[0].description}</p>
        `;

        weeklyForecastElement.appendChild(forecastCard);
    });
}

function groupForecastByDay(forecastList) {
    const groupedForecast = {};

    forecastList.forEach(forecast => {
        const date = new Date(forecast.dt * 1000);
        const day = date.getDate();

        if (!groupedForecast[day]) {
            groupedForecast[day] = [];
        }
        groupedForecast[day].push(forecast);
    });

    return groupedForecast;
}
