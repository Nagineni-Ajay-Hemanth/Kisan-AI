
import sys
import os
import json
import unittest

# Add current directory to path to import local modules
sys.path.append(os.getcwd())

try:
    from ai_advice import AgriAdvisor
except ImportError:
    print("Error: Could not import AgriAdvisor from ai_advice.py")
    sys.exit(1)

class TestTranslation(unittest.TestCase):
    
    def test_ai_lang_param(self):
        print("\n--- Testing AgriAdvisor Language Support ---")
        
        # Test Case: Hindi
        input_data = {
            "past_soil_type": "Clay",
            "present_plant_condition": "Blight",
            "crop": "Potato",
            "language": "hi"
        }
        
        # We can't easily verify the *output* language without an actual LLM call (which we have), 
        # but we can verify it doesn't crash and returns expected keys.
        # Ideally, we'd mock the LLM, but here we are testing the integration.
        
        output = AgriAdvisor.generate_advice(input_data)
        
        print("Hindi Advice Output Keys:", output.keys())
        self.assertIn("advice", output)
        
        # Check if fallback logic was used (if LLM fails) or real output.
        # Note: If LLM fails, fallback logic currently returns English. 
        # Real verification relies on LLM connectivity.
        
        if "advice" in output:
             print("Advice received.")

if __name__ == "__main__":
    unittest.main()
