"""
Sanity tests for external services (Open-Meteo Weather Service).
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.weather_service import WeatherService

def test_weather_service():
    # Test coordinates for Dallas, TX
    res = WeatherService.get_route_weather(32.7767, -96.7970)
    assert "ambient_temp_c" in res
    assert res["latitude"] == 32.7767
    print(f"Weather API Test Passed: {res}")

if __name__ == "__main__":
    test_weather_service()

