from google import genai
import os

API_KEY = "AIzaSyCq0ejAwUG2awm6bTfkreP_lthdxkbEwJI"
client = genai.Client(api_key=API_KEY)

try:
    print("Testing Gemini 2.5 Flash...")
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents="Hello, represent yourself."
    )
    print("Success 2.5:", response.text)
except Exception as e:
    print("Failed 2.5:", e)

try:
    print("\nTesting Gemini 1.5 Flash...")
    response = client.models.generate_content(
        model='gemini-1.5-flash', 
        contents="Hello, represent yourself."
    )
    print("Success 1.5:", response.text)
except Exception as e:
    print("Failed 1.5:", e)
