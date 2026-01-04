import pytest
import pandas as pd
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@pytest.fixture
def api_params():
    return {
        "latitude": 43.65107,     # Toronto
        "longitude": -79.347015,
        "hourly": [
            "precipitation",
            "precipitation_probability",
            "temperature_2m"
        ],
        "timezone": "UTC"
    }


def test_api_returns_200(api_params):
    """API should return HTTP 200"""
    response = requests.get(OPEN_METEO_URL, params=api_params)
    assert response.status_code == 200


def test_response_is_valid_json(api_params):
    """Response must be valid JSON"""
    response = requests.get(OPEN_METEO_URL, params=api_params)
    data = response.json()
    assert isinstance(data, dict)


def test_mandatory_fields_exist(api_params):
    """Ensure mandatory fields are present"""
    response = requests.get(OPEN_METEO_URL, params=api_params)
    data = response.json()

    assert "hourly" in data
    assert "time" in data["hourly"]
    assert "precipitation" in data["hourly"]
    assert "precipitation_probability" in data["hourly"]
    assert "temperature_2m" in data["hourly"]


def test_no_negative_weather_values(api_params):
    """Weather values should not be negative"""
    response = requests.get(OPEN_METEO_URL, params=api_params)
    hourly = response.json()["hourly"]

    df = pd.DataFrame({
        "precipitation": hourly["precipitation"],
        "precip_probability": hourly["precipitation_probability"],
        "temperature": hourly["temperature_2m"]
    })

    # precipitation & probability must be >= 0
    assert (df["precipitation"] >= 0).all()
    assert (df["precip_probability"] >= 0).all()
