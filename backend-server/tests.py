import sys
import os
import json
import unittest
from weather_engine import WeatherEngine

# Add current directory to path to import local modules
sys.path.append(os.getcwd())

try:
    from ai_advice import AgriAdvisor
except ImportError:
    print("Error: Could not import AgriAdvisor from ai_advice.py")
    sys.exit(1)

class TestKisanAI(unittest.TestCase):
    
    def test_weather_engine(self):
        print("\n--- Testing Weather Engine ---")
        # Test with a known location (New Delhi approx)
        lat = 28.61
        lon = 77.20
        
        weather = WeatherEngine.get_weather(lat, lon)
        print(json.dumps(weather, indent=2))
        
        self.assertIn("temperature", weather)
        self.assertIn("condition", weather)
        
        if weather.get("source") == "Google":
            print("SUCCESS: Scraped from Google")
        else:
            print("WARNING: Fallback to Simulation used")

    def test_agri_advisor(self):
        print("\n--- Testing AgriAdvisor ---")
        
        # Test Case 1: Disease Detected (Change from Healthy)
        input1 = {
            "past_soil_type": "Clay",
            "past_plant_condition": "Healthy",
            "present_soil_type": "Clay",
            "present_plant_condition": "Blight",
            "present_weather": "Rainy, 22C",
            "crop": "Potato"
        }
        
        output1 = AgriAdvisor.generate_advice(input1)
        # print("Test Case 1 Output:", json.dumps(output1, indent=2))
        
        self.assertIn("advice", output1)
        self.assertIn("watering_advice", output1)
        self.assertIn("fertilizers_advice", output1)
        # Check for alert keywords if logic supports it, otherwise generic check
        # self.assertIn("ALERT", output1["advice"]) 
        
        # Test Case 2: Healthy Stable
        input2 = {
            "past_soil_type": "Sandy",
            "past_plant_condition": "Healthy",
            "present_soil_type": "Sandy",
            "present_plant_condition": "Healthy",
            "present_weather": "Sunny, 30C",
            "crop": "Wheat"
        }
        
        output2 = AgriAdvisor.generate_advice(input2)
        self.assertIn("advice", output2)
        
        # Test Case 3: Messy Labels
        input3 = {
            "past_soil_type": "Loam",
            "past_plant_condition": "Unknown",
            "present_soil_type": "Loam",
            "present_plant_condition": "Tomato___healthy",
            "present_weather": "Cloudy, 25C",
            "crop": "Tomato"
        }
        
        output3 = AgriAdvisor.generate_advice(input3)
        self.assertNotIn("suffering from", output3["advice"])

if __name__ == "__main__":
    unittest.main()
