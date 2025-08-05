import os
from datetime import datetime

import requests

API_KEY = "67cc2ef2e5195ccb3be69bb343f18f83"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
SAVE_FILE = "last_weather.txt"

def get_coordinates(city, state=None, country="US"):
    location = f"{city},{state},{country}" if state else f"{city},{country}"
    params = {
        "q": location,
        "limit": 1,
        "appid": API_KEY
    }
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"], data[0]["name"]
        else:
            print("Location not found.")
            return None, None, None
    except requests.exceptions.RequestException as err:
        print(f"Geocoding error: {err}")
        return None, None, None

def get_weather_data(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        print("Weather API error.")
        return None

def get_forecast_data(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Forecast error: {err}")
        return None

def convert_temperature(temp_celsius, to_unit="F"):
    if to_unit.upper() == "F":
        return round((temp_celsius * 9/5) + 32, 2)
    return temp_celsius

def convert_wind_speed(speed_mps, to_unit="mph"):
    if to_unit.lower() == "mph":
        return round(speed_mps * 2.23694, 2)
    return speed_mps

def display_weather(data, unit="C"):
    if not data:
        print("No data to display.")
        return None

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    condition = data["weather"][0]["description"]

    if unit.upper() == "F":
        temp = convert_temperature(temp, "F")
    wind_mph = convert_wind_speed(wind, "mph")

    print(f"\n Current Weather:")
    print(f"Temperature: {temp}°{unit.upper()}")
    print(f"Condition: {condition.capitalize()}")
    print(f"Humidity: {humidity}%")
    print(f"Wind Speed: {wind_mph} mph\n")

    return f"{temp}°{unit.upper()}, {condition.capitalize()}, {humidity}%, {wind_mph} mph"

def display_forecast(forecast_data, unit="C"):
    if not forecast_data:
        print("No forecast data available.")
        return

    print("3-Day Forecast:")
    daily_summary = {}

    for entry in forecast_data["list"]:
        date_str = entry["dt_txt"].split(" ")[0]
        temp = entry["main"]["temp"]
        condition = entry["weather"][0]["description"]

        if date_str not in daily_summary:
            daily_summary[date_str] = {
                "temps": [],
                "conditions": []
            }

        daily_summary[date_str]["temps"].append(temp)
        daily_summary[date_str]["conditions"].append(condition)

    count = 0
    for date_str, info in daily_summary.items():
        if count >= 3:
            break
        high = max(info["temps"])
        low = min(info["temps"])
        condition = max(set(info["conditions"]), key=info["conditions"].count)

        if unit.upper() == "F":
            high = convert_temperature(high, "F")
            low = convert_temperature(low, "F")

        date_fmt = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        print(f"{date_fmt}: {condition.capitalize()}, High: {round(high, 1)}°, Low: {round(low, 1)}°{unit.upper()}")
        count += 1

def save_last_search(city, state, summary):
    with open(SAVE_FILE, "w") as f:
        f.write(f"{city},{state}\n{summary}")

def load_last_search():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                location = lines[0].strip()
                summary = lines[1].strip()
                print(f"\n Last Search: {location}")
                print(f"Weather: {summary}\n")

def main_menu():
    print("\n--- Tempulon Basic ---")
    load_last_search()

    while True:
        city = input("Enter city name (or 'exit' to quit): ").strip()
        if city.lower() == "exit":
            print("Goodbye!")
            break
        if not city:
            print("Please enter a valid city name.")
            continue

        state = input("Enter 2-letter state code (optional): ").strip()
        unit = input("Choose temperature unit - C or F: ").strip().upper()
        if unit not in ["C", "F"]:
            print("Invalid unit. Defaulting to Celsius.")
            unit = "C"

        lat, lon, resolved_city = get_coordinates(city, state)
        if lat is None or lon is None:
            continue

        weather_data = get_weather_data(lat, lon)
        print(f"\n Location: {resolved_city}, {state.upper() if state else ''}")
        summary = display_weather(weather_data, unit)

        forecast_data = get_forecast_data(lat, lon)
        display_forecast(forecast_data, unit)

        if summary:
            save_last_search(resolved_city, state.upper() if state else "", summary)

if __name__ == "__main__":
    main_menu()