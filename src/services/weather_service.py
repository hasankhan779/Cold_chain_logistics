"""
Open-Meteo Weather Service.
Free external REST API to fetch live route and transit ambient weather conditions.
"""
import requests
from typing import Dict, Any
from src.config.settings import settings

class WeatherService:
    @staticmethod
    def get_route_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
            "forecast_days": 1
        }
        try:
            response = requests.get(settings.OPEN_METEO_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            return {
                "latitude": latitude,
                "longitude": longitude,
                "ambient_temp_c": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "weather_code": current.get("weather_code")
            }
        except Exception as e:
            return {"error": f"Failed to retrieve weather for ({latitude}, {longitude}): {str(e)}"}

