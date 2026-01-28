import random
import hashlib
import requests
from datetime import datetime
from bs4 import BeautifulSoup

class WeatherEngine:
    @staticmethod
    def get_weather(lat: float, lon: float) -> dict:
        """
        Get real weather from Open-Meteo (Free, No Key). Fallback to simulation.
        """
        try:
            # Open-Meteo is free for non-commercial use and requires no API key.
            # It is much more reliable than scraping Google.
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if "current_weather" in data:
                cw = data["current_weather"]
                temp = cw["temperature"]
                wmo_code = cw["weathercode"]
                wind_speed = cw["windspeed"]
                
                # Map WMO code to condition text
                condition = WeatherEngine._get_wmo_condition(wmo_code)
                
                # OpenMeteo current_weather doesn't give humidity, so we estimate or fetch hourly
                # For simplicity in this "lite" engine, we'll simulate humidity based on condition
                # or fetch from 'hourly' if we wanted to be perfect. Let's keep it simple/fast.
                humidity = 80 if "Rain" in condition else 45
                
                # Rain chance map
                rain_chance = 80 if "Rain" in condition or "Drizzle" in condition else 10
                
                return {
                    "temperature": int(temp),
                    "condition": condition,
                    "humidity": humidity,
                    "wind_speed": int(wind_speed),
                    "rain_chance": rain_chance,
                    "location": f"{round(lat, 2)}, {round(lon, 2)}",
                    "source": "OpenMeteo"
                }
                
            raise Exception("Invalid OpenMeteo response")

        except Exception as e:
            print(f"Weather API Failed: {e}")
            print("Falling back to simulation.")
            return WeatherEngine._simulate_weather(lat, lon)

    @staticmethod
    def _get_wmo_condition(code):
        # WMO Weather interpretation codes (WW)
        if code == 0: return "Clear Sky"
        if code in [1, 2, 3]: return "Partly Cloudy"
        if code in [45, 48]: return "Foggy"
        if code in [51, 53, 55]: return "Drizzle"
        if code in [61, 63, 65]: return "Rainy"
        if code in [71, 73, 75]: return "Snow"
        if code in [80, 81, 82]: return "Heavy Rain"
        if code in [95, 96, 99]: return "Thunderstorm"
        return "Cloudy" # Default fallback

    @staticmethod
    def _simulate_weather(lat: float, lon: float) -> dict:
        """
        Fallback: Deterministic simulation
        """
        # Use date and location to seed random number generator
        today = datetime.now().strftime("%Y-%m-%d")
        seed_str = f"{today}-{round(lat, 2)}-{round(lon, 2)}"
        
        # Create a deterministic hash integer
        seed_int = int(hashlib.sha256(seed_str.encode('utf-8')).hexdigest(), 16) % 10**8
        random.seed(seed_int)
        
        month = datetime.now().month
        hour = datetime.now().hour
        
        # Base settings
        if month in [3, 4, 5]: # Summer
            base_temp = 32
            conditions = ["Sunny", "Sunny", "Partly Cloudy", "Hot"]
        elif month in [6, 7, 8, 9]: # Monsoon
            base_temp = 28
            conditions = ["Rainy", "Cloudy", "Heavy Rain", "Drizzle"]
        elif month in [10, 11]: # Post-Monsoon
            base_temp = 25
            conditions = ["Clear", "Partly Cloudy", "Sunny"]
        else: # Winter
            base_temp = 18
            conditions = ["Clear", "Foggy", "Sunny", "Cold"]
            
        time_offset = -abs(hour - 14) / 2
        final_temp = base_temp + time_offset + random.randint(-2, 3)
        condition = random.choice(conditions)
        
        if "Rain" in condition or "Drizzle" in condition:
            humidity = random.randint(80, 95)
            wind_speed = random.randint(10, 25)
        elif "Sunny" in condition or "Hot" in condition:
            humidity = random.randint(20, 50)
            wind_speed = random.randint(5, 15)
        else:
            humidity = random.randint(50, 75)
            wind_speed = random.randint(5, 12)

        rain_chance = 0
        if "Rain" in condition: rain_chance = random.randint(70, 100)
        elif "Cloudy" in condition: rain_chance = random.randint(30, 60)
        else: rain_chance = random.randint(0, 20)
        
        return {
            "temperature": int(final_temp),
            "condition": condition,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "rain_chance": rain_chance,
            "location": f"{round(lat, 2)}, {round(lon, 2)}",
            "source": "Simulation"
        }
