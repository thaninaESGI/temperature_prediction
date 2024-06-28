import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime, timedelta

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define the location for Paris
latitude = 48.8566
longitude = 2.3522

# Initialize an empty DataFrame to store the data
all_data = pd.DataFrame()

# Loop over the last 4 years
for year in range(4):
    end_date = (datetime.now() - timedelta(days=year*365)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=(year+1)*365)).strftime('%Y-%m-%d')
    
    # Define the parameters for the API request
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    
    # Process the response
    response = responses[0]
    print(f"Processing data from {start_date} to {end_date}")
    
    # Process hourly data
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
    
    # Append the data to the main DataFrame
    all_data = pd.concat([all_data, hourly_dataframe], ignore_index=True)

# Print the number of rows in the DataFrame
print(f"Total number of rows: {len(all_data)}")

# Save the data to a CSV file
output_file = "paris_weather_data_4_years.csv"
all_data.to_csv(output_file, index=False)
print(f"Data has been saved to {output_file}")