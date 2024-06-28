import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime, timedelta
import os

def fetch_weather_data(save_path, df_path):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    url = "https://archive-api.open-meteo.com/v1/archive"
    yesterday = datetime.now() - timedelta(2)
    start_date = yesterday.strftime("%Y-%m-%d")
    end_date = start_date
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe.to_csv(f"./{save_path}", index=False)
    return save_path

def update_dataframe_with_new_data(new_df, save_path, df_path):
    existing_data_file = os.path.join(save_path, df_path)

    # Assurez-vous que le répertoire parent existe
    os.makedirs(os.path.dirname(existing_data_file), exist_ok=True)

    if os.path.exists(existing_data_file):
        existing_df = pd.read_csv(existing_data_file)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df.copy()

    combined_df.to_csv(existing_data_file, index=False)
