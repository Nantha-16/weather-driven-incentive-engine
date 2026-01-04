import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime

class WeatherClient:
    def __init__(self, cache_ttl=3600):
        cache_session = requests_cache.CachedSession(
            '.cache', expire_after=cache_ttl
        )
        retry_session = retry(cache_session, retries=3, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)

    def fetch_weather(self, lat, lon):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": [
                "precipitation",
                "precipitation_probability",
                "temperature_2m"
            ]
        }

        response = self.client.weather_api(url, params=params)[0]
        hourly = response.Hourly()

        data = {
            "time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                periods=len(hourly.Variables(0).ValuesAsNumpy()),
                freq="H"
            ),
            "precipitation": hourly.Variables(0).ValuesAsNumpy(),
            "precip_probability": hourly.Variables(1).ValuesAsNumpy(),
            "temperature": hourly.Variables(2).ValuesAsNumpy()
        }
        

        return pd.DataFrame(data)
