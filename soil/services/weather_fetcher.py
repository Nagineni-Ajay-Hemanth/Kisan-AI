
import requests
import logging
from typing import Dict, Optional
from config import Config

class WeatherFetcher:
    def __init__(self, api_key: str = Config.OPENWEATHER_API_KEY):
        self.api_key = api_key
        if api_key == 'your_api_key_here':
            logging.warning("Using default OpenWeatherMap API key. Replace with your own.")
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather data"""
        try:
            url = f"{Config.OPENWEATHER_BASE_URL}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed']
            }
            
        except Exception as e:
            logging.error(f"Error fetching current weather: {str(e)}")
            # Return mock data for testing
            return {
                'temperature': 28.5,
                'humidity': 65.0,
                'pressure': 1013.0,
                'description': 'clear sky',
                'wind_speed': 3.5
            }
    
    def get_historical_rainfall(self, lat: float, lon: float, days: int = 5) -> Optional[float]:
        """Get historical rainfall data"""
        try:
            url = f"{Config.OPENWEATHER_BASE_URL}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': 40
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            total_rain = 0.0
            for forecast in data['list']:
                if 'rain' in forecast:
                    rain_mm = forecast['rain'].get('3h', 0)
                    total_rain += rain_mm
            
            avg_daily_rain = total_rain / (len(data['list']) / 8)
            
            return avg_daily_rain
            
        except Exception as e:
            logging.error(f"Error fetching rainfall data: {str(e)}")
            # Return default value
            return 10.0
    
    def get_weather_adjustments(self, lat: float, lon: float) -> Dict[str, float]:
        """Get weather-based adjustment factors for soil analysis"""
        
        current_weather = self.get_current_weather(lat, lon)
        avg_rainfall = self.get_historical_rainfall(lat, lon, days=5)
        
        adjustments = {
            'sandy_reduction': 0.0,
            'clay_crack_increase': 0.0,
            'texture_reliability': 1.0,
            'color_bias_reliability': 1.0
        }
        
        if current_weather:
            temp = current_weather['temperature']
            humidity = current_weather['humidity']
            
            # Rule 1: If rain > 20mm → reduce sandy score
            if avg_rainfall > 20:
                adjustments['sandy_reduction'] = min(0.3, (avg_rainfall - 20) / 50)
            
            # Rule 2: If temp > 35 → increase clay crack score
            if temp > 35:
                adjustments['clay_crack_increase'] = min(0.4, (temp - 35) / 20)
            
            # Rule 3: If humidity > 70 → reduce texture reliability
            if humidity > 70:
                adjustments['texture_reliability'] = max(0.5, 1.0 - (humidity - 70) / 60)
            
            # Additional rule
            if humidity > 80:
                adjustments['color_bias_reliability'] = 0.7
        
        return {
            'adjustments': adjustments,
            'weather_data': current_weather or {},
            'avg_rainfall_5days_mm': avg_rainfall
        }
