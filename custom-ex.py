import os
import time
import math
import random
import requests
from prometheus_client import start_http_server, Gauge

# === Configuration ===
API_TOKEN = os.getenv("OWM_API_KEY", "")
CITY_NAME = os.getenv("CITY_NAME", "Astana")
UNIT_SYSTEM = os.getenv("UNIT_SYSTEM", "metric")  # metric | imperial
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "20"))  # seconds

WEATHER_URL = (
    f"https://api.openweathermap.org/data/2.5/weather?"
    f"q={CITY_NAME}&appid={API_TOKEN}&units={UNIT_SYSTEM}"
)

# === Metric Definitions ===
gauges = {
    "temp": Gauge("weather_temp_celsius", "Current air temperature", ["city"]),
    "feels": Gauge("weather_feelslike_celsius", "Feels-like temperature", ["city"]),
    "press": Gauge("weather_pressure_hpa", "Atmospheric pressure", ["city"]),
    "humid": Gauge("weather_humidity_percent", "Relative humidity", ["city"]),
    "wind_speed": Gauge("weather_wind_speed_ms", "Wind speed (m/s)", ["city"]),
    "wind_dir": Gauge("weather_wind_dir_deg", "Wind direction (degrees)", ["city"]),
    "clouds": Gauge("weather_cloudiness_percent", "Cloud cover (%)", ["city"]),
    "visibility": Gauge("weather_visibility_m", "Visibility in meters", ["city"]),
    "rain": Gauge("weather_rain_1h_mm", "Rainfall in the last hour (mm)", ["city"]),
    "snow": Gauge("weather_snow_1h_mm", "Snowfall in the last hour (mm)", ["city"]),
    "sunrise": Gauge("weather_sunrise_time", "Sunrise timestamp (UNIX)", ["city"]),
    "sunset": Gauge("weather_sunset_time", "Sunset timestamp (UNIX)", ["city"]),
}

# === Helper Functions ===
def update_metrics(data: dict):
    """Extract and update metric values from JSON data."""
    city = data.get("name", CITY_NAME)
    main = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    sys_info = data.get("sys", {})
    rain = data.get("rain", {})
    snow = data.get("snow", {})

    gauges["temp"].labels(city).set(main.get("temp", float("nan")))
    gauges["feels"].labels(city).set(main.get("feels_like", float("nan")))
    gauges["press"].labels(city).set(main.get("pressure", float("nan")))
    gauges["humid"].labels(city).set(main.get("humidity", float("nan")))
    gauges["wind_speed"].labels(city).set(wind.get("speed", float("nan")))
    gauges["wind_dir"].labels(city).set(wind.get("deg", float("nan")))
    gauges["clouds"].labels(city).set(clouds.get("all", float("nan")))
    gauges["visibility"].labels(city).set(data.get("visibility", float("nan")))
    gauges["rain"].labels(city).set(rain.get("1h", 0.0))
    gauges["snow"].labels(city).set(snow.get("1h", 0.0))
    gauges["sunrise"].labels(city).set(sys_info.get("sunrise", 0))
    gauges["sunset"].labels(city).set(sys_info.get("sunset", 0))

def fake_weather_data(timestamp: float):
    """Generate pseudo weather data when no API key is available."""
    temperature = 12 + 8 * math.sin(timestamp / 180) + random.uniform(-1, 1)
    feels_like = temperature - random.uniform(0.0, 1.2)
    pressure = 1013 + random.uniform(-10, 10)
    humidity = max(25, min(90, 60 + random.uniform(-20, 20)))
    wind_speed = max(0, 3 + random.uniform(-1, 2))
    wind_dir = random.uniform(0, 360)
    cloudiness = max(0, min(100, 50 + random.uniform(-40, 40)))
    visibility = max(2000, 10000 + random.uniform(-1000, 1000))
    rain = random.choice([0, 0, 0, 0.3, 0.7]) * random.random()
    snow = 0.0
    sunrise = int(time.time()) - (int(time.time()) % 86400) + 7 * 3600
    sunset = int(time.time()) - (int(time.time()) % 86400) + 18 * 3600

    data = {
        "name": CITY_NAME,
        "main": {"temp": temperature, "feels_like": feels_like, "pressure": pressure, "humidity": humidity},
        "wind": {"speed": wind_speed, "deg": wind_dir},
        "clouds": {"all": cloudiness},
        "visibility": visibility,
        "rain": {"1h": rain},
        "snow": {"1h": snow},
        "sys": {"sunrise": sunrise, "sunset": sunset},
    }
    update_metrics(data)

def collect_weather():
    """Pull real weather data from OpenWeather API or generate fake data."""
    if not API_TOKEN:
        fake_weather_data(time.time())
        return
    try:
        response = requests.get(WEATHER_URL, timeout=10)
        if response.status_code == 200:
            payload = response.json()
            if "main" in payload:
                update_metrics(payload)
                return
        # Fallback if bad response or missing keys
        fake_weather_data(time.time())
    except Exception as err:
        print("Weather fetch failed:", err)
        fake_weather_data(time.time())

# === Main Loop ===
if __name__ == "__main__":
    start_http_server(8000)
    print(f"🌤️  Weather exporter running on http://localhost:8000/metrics (city={CITY_NAME})")
    while True:
        collect_weather()
        time.sleep(UPDATE_INTERVAL)
