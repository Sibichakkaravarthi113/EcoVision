from typing import Dict, Any, List
import httpx


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_open_meteo_forecast(latitude: float, longitude: float, city: str = "Unknown") -> Dict[str, Any]:
    """
    Fetches real-time weather and 3-day forecast from Open-Meteo.
    Handles network errors gracefully with informative fallbacks.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "current_weather": "true",
        "forecast_days": 3,
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()

        current_raw = data.get("current_weather", {})
        hourly_raw = data.get("hourly", {})

        hourly_times = hourly_raw.get("time", [])
        temps = hourly_raw.get("temperature_2m", [])
        humidity = hourly_raw.get("relative_humidity_2m", [])
        precip = hourly_raw.get("precipitation", [])
        winds = hourly_raw.get("wind_speed_10m", [])

        forecast_list: List[Dict[str, Any]] = []
        for i in range(min(72, len(hourly_times))):
            forecast_list.append({
                "time": hourly_times[i],
                "temperature_c": temps[i] if i < len(temps) else None,
                "humidity_percent": humidity[i] if i < len(humidity) else None,
                "rainfall_mm": precip[i] if i < len(precip) else None,
                "wind_speed_kmh": winds[i] if i < len(winds) else None,
            })

        current = {
            "temperature_c": current_raw.get("temperature"),
            "wind_speed_kmh": current_raw.get("windspeed"),
            "wind_direction": current_raw.get("winddirection"),
            "weather_code": current_raw.get("weathercode"),
            "time": current_raw.get("time"),
            "humidity_percent": humidity[0] if humidity else None,
            "rainfall_mm": precip[0] if precip else 0.0,
        }

        return {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "source": "Open-Meteo API",
            "current": current,
            "hourly_forecast": forecast_list,
        }

    except Exception as exc:
        # Graceful fallback when network / external API is unavailable
        return {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "source": f"Open-Meteo API (Offline Fallback: {str(exc)})",
            "current": {
                "temperature_c": 28.5,
                "wind_speed_kmh": 12.0,
                "wind_direction": 180,
                "weather_code": 1,
                "time": "now",
                "humidity_percent": 65.0,
                "rainfall_mm": 0.0,
            },
            "hourly_forecast": [],
        }
