import random
from google import genai
import json
import os

# Configure Generative AI Client
API_KEY = "AIzaSyCZDN_eHK8fb5dgJIv8RwC-SKReApbqAdk"
client = genai.Client(api_key=API_KEY)

class AgriAdvisor:
    @staticmethod
    def generate_advice(input_data: dict) -> dict:
        """
        Generates structured agricultural advice using Gemini API (New SDK).
        """
        
        # Extract inputs for Fallback Logic (if API fails)
        past_soil = input_data.get("past_soil_type", "Unknown")
        curr_soil = input_data.get("present_soil_type", "Unknown")
        curr_cond_raw = input_data.get("present_plant_condition", "Unknown")
        weather = input_data.get("present_weather", "Sunny")
        crop = input_data.get("crop", "Crop")
        
        # Extract language
        language_code = input_data.get("language", "en")
        language_map = {
            "en": "English", "hi": "Hindi", "te": "Telugu", "bn": "Bengali", 
            "mr": "Marathi", "ta": "Tamil", "gu": "Gujarati", "kn": "Kannada", 
            "ml": "Malayalam", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
            "ur": "Urdu"
        }
        target_lang = language_map.get(language_code, "English")

        try:
            # --- GEMINI API CALL (New SDK) ---
            # Using stable Flash model. 
            
            prompt = f"""
            You are an expert agricultural scientist named "Kisan AI".
            
            Analyze the following farm data and provide specific, actionable advice for an Indian farmer.
            
            Context:
            - Crop: {crop}
            - Current Weather: {weather}
            - Soil Type: {curr_soil} (Previous: {past_soil})
            - Plant Health Condition: {curr_cond_raw}
            
            Task:
            Provide advice in 3 distinct sections. 
            CRITICAL: BE EXTREMELY CONCISE. Use short bullet points. Max 2-3 sentences per section.
            
            **IMPORTANT: Output MUST be in {target_lang} language.**
            
            1. General Advice: Plant health actions.
            2. Watering Plan: Schedule based on {weather}.
            3. Fertilizer Recommendation: Specific nutrients.
            
            Format:
            Return ONLY a valid JSON object with keys: "advice", "watering_advice", "fertilizers_advice".
            Do not include Markdown formatting.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt
            )
            
            # Clean response text (remove potential markdown blocks)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            json_output = json.loads(raw_text)
            
            # Safe get
            return {
                "advice": json_output.get("advice", "Review crop health regularly."),
                "watering_advice": json_output.get("watering_advice", "Water according to soil moisture."),
                "fertilizers_advice": json_output.get("fertilizers_advice", "Use balanced fertilizers.")
            }
            
        except Exception as e:
            print(f"Gemini API Failed: {e}")
            print("Falling back to Rule-Based Logic")
            return AgriAdvisor._fallback_logic(input_data)

    @staticmethod
    def _fallback_logic(input_data):
        # Extract inputs with defaults
        past_soil = input_data.get("past_soil_type", "Unknown")
        curr_soil = input_data.get("present_soil_type", "Unknown")
        curr_cond_raw = input_data.get("present_plant_condition", "Unknown")
        weather = input_data.get("present_weather", "Sunny")
        crop = input_data.get("crop", "Crop")
        lang = input_data.get("language", "en")

        # --- Translations ---
        translations = {
            "en": {
                "monitor": "Monitor {crop} closely in {weather} weather.",
                "treat": "Treat {condition} immediately.",
                "healthy": "Your crop looks healthy.",
                "rain": "Suspend watering due to rain.",
                "water_reg": "Water regularly to maintain moisture.",
                "fertilizer": "Apply balanced NPK fertilizer."
            },
            "hi": {
                "monitor": "{weather} मौसम में {crop} की बारीकी से निगरानी करें।",
                "treat": "{condition} का तुरंत उपचार करें।",
                "healthy": "आपकी फसल स्वस्थ दिख रही है।",
                "rain": "बारिश के कारण पानी देना बंद करें।",
                "water_reg": "नमी बनाए रखने के लिए नियमित रूप से पानी दें।",
                "fertilizer": "संतुलित NPK खाद का प्रयोग करें।"
            },
            "te": {
                "monitor": "{weather} వాతావరణంలో {crop} ను జాగ్రత్తగా గమనించండి.",
                "treat": "{condition} కు వెంటనే చికిత్స చేయండి.",
                "healthy": "మీ పంట ఆరోగ్యంగా ఉంది.",
                "rain": "వర్షం కారణంగా నీరు పెట్టడం ఆపండి.",
                "water_reg": "తేమను నిర్వహించడానికి క్రమం తప్పకుండా నీరు పెట్టండి.",
                "fertilizer": "సమతుల్య NPK ఎరువును వాడండి."
            }
        }
        
        # Default to English if lang not found
        t = translations.get(lang, translations["en"])

        advice_parts = []
        watering_parts = []
        fertilizer_parts = []
        
        # Simple Logic
        advice_parts.append(t["monitor"].format(crop=crop, weather=weather))
        
        if "healthy" not in curr_cond_raw.lower():
            advice_parts.append(t["treat"].format(condition=curr_cond_raw))
        else:
             advice_parts.append(t["healthy"])

        if "rain" in weather.lower():
            watering_parts.append(t["rain"])
        else:
            watering_parts.append(t["water_reg"])
            
        fertilizer_parts.append(t["fertilizer"])

        return {
            "advice": " ".join(advice_parts),
            "watering_advice": " ".join(watering_parts),
            "fertilizers_advice": " ".join(fertilizer_parts)
        }
