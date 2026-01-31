
import os
import cv2
import numpy as np
from config import Config
from services.map_reader import MapReader
from services.weather_fetcher import WeatherFetcher
from services.image_analyzer import ImageAnalyzer
from services.decision_engine import DecisionEngine

def cli_interface():
    """Command line interface for testing"""
    print("=" * 60)
    print("Soil Estimation System - Command Line Interface")
    print("=" * 60)
    
    # Get GPS coordinates
    print("\nEnter GPS Coordinates (Telangana Region):")
    try:
        lat_input = input("Latitude (15.8361 to 19.9178) [Default: 17.3850]: ").strip()
        lat = float(lat_input) if lat_input else 17.3850
        
        lon_input = input("Longitude (77.2356 to 81.3211) [Default: 78.4867]: ").strip()
        lon = float(lon_input) if lon_input else 78.4867
        
        # Validate coordinates
        if not (Config.LAT_BOTTOM <= lat <= Config.LAT_TOP):
            print(f"Latitude out of bounds! Must be between {Config.LAT_BOTTOM} and {Config.LAT_TOP}")
            return
        if not (Config.LON_LEFT <= lon <= Config.LON_RIGHT):
            print(f"Longitude out of bounds! Must be between {Config.LON_LEFT} and {Config.LON_RIGHT}")
            return
        
        # Get image path
        image_path = input("\nEnter soil image path (or press Enter to create dummy): ").strip()
        
        if not image_path:
            # Create a dummy image for testing
            image_path = "test_soil_cli.jpg"
            # Create a simple colored image
            img = np.zeros((300, 300, 3), dtype=np.uint8)
            img[:,:] = [100, 150, 80]  # Brownish color
            cv2.imwrite(image_path, img)
            print(f"Created dummy image: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return
        
        print("\nProcessing...")
        
        # Initialize modules
        map_reader = MapReader()
        image_analyzer = ImageAnalyzer()
        weather_fetcher = WeatherFetcher()
        decision_engine = DecisionEngine()
        
        # Process
        soil_scores = image_analyzer.analyze_soil_image(image_path)
        map_data = map_reader.get_land_info(lat, lon)
        print("Fetching weather data...")
        weather_data = weather_fetcher.get_weather_adjustments(lat, lon)
        
        result = decision_engine.determine_soil_type(
            soil_scores=soil_scores,
            map_data=map_data,
            weather_data=weather_data,
            location={'lat': lat, 'lon': lon}
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("SOIL ANALYSIS RESULTS")
        print("=" * 60)
        print(f"Winning Soil Type: {result['soil_type']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Land Class (Map): {result['land_class']}")
        print("-" * 30)
        print("Detailed Scores:")
        for soil, score in result['final_scores'].items():
            print(f"  {soil}: {score:.3f}")
        
        print("-" * 30)
        print("Analysis Reasoning:")
        for reason in result['reason']:
            print(f"  - {reason}")
        print("=" * 60)
        
        # Clean up dummy file if created
        if image_path == "test_soil_cli.jpg":
            try:
                os.remove(image_path)
                print("(Dummy test image removed)")
            except:
                pass

    except ValueError as e:
        print(f"Error: Invalid input - {e}")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    cli_interface()
