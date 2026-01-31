
import os
import cv2
import numpy as np
import logging
import requests
from typing import Dict, List, Optional, Tuple

class SoilEngine:
    # --- CONFIG ---
    # Map boundaries for Telangana
    LAT_TOP = 19.9178
    LAT_BOTTOM = 15.8361
    LON_LEFT = 77.2356
    LON_RIGHT = 81.3211

    # OpenWeatherMap API
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '0eb1b6f980c80a0423e9c9cb1f13d9b0')
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    # Color to Land Class Mapping with ±20 tolerance
    COLOR_CLASSES = {
        'forest': {
            'range': [(30, 120, 30), (90, 200, 90)],  # RGB: Green
            'land_class': 'Forest',
            'soil_bias': {'Loamy': 0.8, 'Clay': 0.1, 'Sandy': 0.1}
        },
        'crop_land': {
            'range': [(180, 180, 0), (255, 255, 80)],  # RGB: Yellow
            'land_class': 'Crop Land',
            'soil_bias': {'Loamy': 0.5, 'ClayLoam': 0.4, 'Sandy': 0.1}
        },
        'barren': {
            'range': [(120, 70, 0), (200, 140, 60)],  # RGB: Brown
            'land_class': 'Barren/Rocky',
            'soil_bias': {'Sandy': 0.6, 'Gravel': 0.3, 'Loamy': 0.1}
        },
        'scrub': {
            'range': [(200, 0, 200), (255, 200, 255)],  # RGB: Pink/Magenta
            'land_class': 'Scrub',
            'soil_bias': {'SandyLoam': 0.7, 'Sandy': 0.2, 'Loamy': 0.1}
        },
        'water': {
            'range': [(0, 0, 180), (100, 100, 255)],  # RGB: Blue
            'land_class': 'Water/Wetland',
            'soil_bias': {'Clay': 0.9, 'Loamy': 0.1}
        },
        'urban': {
            'range': [(180, 0, 0), (255, 60, 60)],  # RGB: Red
            'land_class': 'Urban/BuiltUp',
            'soil_bias': {'Mixed': 1.0}
        }
    }

    def __init__(self):
        """Initialize the SoilEngine with resources"""
        # Load Map
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.map_path = os.path.join(current_dir, 'TS.png')
        self.map_image = cv2.imread(self.map_path)
        
        if self.map_image is None:
            logging.warning(f"Map file {self.map_path} not found. Using reduced functionality.")
            self.height, self.width = 0, 0
        else:
            self.height, self.width = self.map_image.shape[:2]
            logging.info(f"Soil Map loaded: {self.width}x{self.height}")

    # --- MAP LOGIC ---
    def gps_to_pixel(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert GPS coordinates to pixel coordinates in the map"""
        if self.map_image is None:
            return 0, 0

        # Clamp coordinates to bounds
        lat_clamped = max(self.LAT_BOTTOM, min(self.LAT_TOP, lat))
        lon_clamped = max(self.LON_LEFT, min(self.LON_RIGHT, lon))
        
        # Calculate pixel coordinates
        x = int((lon_clamped - self.LON_LEFT) / (self.LON_RIGHT - self.LON_LEFT) * self.width)
        y = int((self.LAT_TOP - lat_clamped) / (self.LAT_TOP - self.LAT_BOTTOM) * self.height)
        
        # Clamp to image dimensions
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        return x, y
    
    def get_pixel_color_region(self, x: int, y: int, region_size: int = 7) -> Tuple[int, int, int]:
        """Get average color of a region around the pixel"""
        if self.map_image is None:
            return (0, 0, 0)

        half_size = region_size // 2
        
        # Define region bounds
        x1 = max(0, x - half_size)
        x2 = min(self.width, x + half_size + 1)
        y1 = max(0, y - half_size)
        y2 = min(self.height, y + half_size + 1)
        
        # Extract region
        region = self.map_image[y1:y2, x1:x2]
        
        # Calculate average color (BGR format)
        if region.size == 0:
            return (0, 0, 0)
            
        avg_color = np.mean(region, axis=(0, 1))
        
        return tuple(map(int, avg_color))
    
    def classify_color(self, color: Tuple[int, int, int]) -> Dict:
        """Classify color into land class with tolerance"""
        b, g, r = color  # OpenCV uses BGR format
        
        for class_name, class_info in self.COLOR_CLASSES.items():
            low_range, high_range = class_info['range']
            
            # Check if color is within tolerance range (RGB format check against config)
            # The config ranges are RGB, so we map r,g,b correctly
            if (low_range[0] <= r <= high_range[0] and
                low_range[1] <= g <= high_range[1] and
                low_range[2] <= b <= high_range[2]):
                
                return {
                    'color_class': class_name,
                    'land_class': class_info['land_class'],
                    'soil_bias': class_info['soil_bias'],
                    'detected_color': (r, g, b)
                }
        
        # Default to unknown if no match
        return {
            'color_class': 'unknown',
            'land_class': 'Unknown',
            'soil_bias': {'Mixed': 1.0},
            'detected_color': (r, g, b)
        }
    
    def get_land_info(self, lat: float, lon: float) -> Dict:
        """Main function to get land information from GPS"""
        if lat is None or lon is None:
             return {'soil_bias': {'Mixed': 1.0}, 'land_class': 'Unknown'}

        x, y = self.gps_to_pixel(lat, lon)
        avg_color = self.get_pixel_color_region(x, y)
        classification = self.classify_color(avg_color)
        
        return {
            'pixel_coords': {'x': x, 'y': y},
            'average_color_rgb': classification['detected_color'],
            'land_class': classification['land_class'],
            'soil_bias': classification['soil_bias'],
            'color_class': classification['color_class']
        }

    # --- WEATHER LOGIC ---
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather data"""
        try:
            url = f"{self.OPENWEATHER_BASE_URL}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            # Note: We don't raise error here to allow fallback
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")
            
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
            return None # Return None to indicate failure/fallback needed upstream

    def get_historical_rainfall(self, lat: float, lon: float, days: int = 5) -> float:
        """Get historical rainfall data estimate"""
        try:
            url = f"{self.OPENWEATHER_BASE_URL}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.OPENWEATHER_API_KEY,
                'units': 'metric',
                'cnt': 40 # 5 days * 8 intervals
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code != 200:
                 return 10.0 # Default fallback

            data = response.json()
            
            total_rain = 0.0
            count = 0
            if 'list' in data:
                for forecast in data['list']:
                    if 'rain' in forecast:
                        rain_mm = forecast['rain'].get('3h', 0)
                        total_rain += rain_mm
                # normalize to daily avg roughly
                avg_daily_rain = total_rain / (len(data['list']) / 8)
                return avg_daily_rain
            return 0.0
            
        except Exception as e:
            logging.error(f"Error fetching rainfall data: {str(e)}")
            return 10.0 # Default value

    def get_weather_adjustments(self, lat: float, lon: float) -> Dict:
        """Get weather-based adjustment factors for soil analysis"""
        if lat is None or lon is None:
            return {'adjustments': {}, 'weather_data': {}}

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
        else:
             # Fallback mock weather if API fails
             current_weather = {'temperature': 25, 'humidity': 50, 'description': 'Unknown'}

        return {
            'adjustments': adjustments,
            'weather_data': current_weather,
            'avg_rainfall_5days_mm': avg_rainfall
        }

    # --- IMAGE ANALYSIS LOGIC ---
    def analyze_image_texture(self, gray_img: np.ndarray) -> Dict[str, float]:
        """Analyze texture features"""
        # Calculate gradient magnitude
        sobelx = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Coarseness measure
        coarseness = np.std(gradient_magnitude) / 255.0
        
        # Homogeneity measure
        _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        homogeneity = np.sum(binary == 255) / (binary.shape[0] * binary.shape[1])
        
        return {
            'coarseness': float(coarseness),
            'homogeneity': float(homogeneity)
        }
    
    def detect_cracks(self, gray_img: np.ndarray) -> float:
        """Detect cracks in soil (common in clay)"""
        # Use Canny edge detection
        edges = cv2.Canny(gray_img, 50, 150)
        
        # Hough Line Transform to detect linear cracks
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=30, maxLineGap=10)
        
        crack_score = 0.0
        if lines is not None:
            total_line_length = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                total_line_length += length
            
            # Normalize by image diagonal
            img_diag = np.sqrt(gray_img.shape[0]**2 + gray_img.shape[1]**2)
            crack_score = min(total_line_length / img_diag, 1.0)
        
        return crack_score
    
    def detect_grains(self, gray_img: np.ndarray) -> float:
        """Detect sand grains using contour analysis"""
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray_img)
        
        # Threshold
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        grain_count = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            # Circularity measure
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter ** 2)
                # Typical grain size range
                if 0.3 < circularity < 1.0 and 10 < area < 1000:
                    grain_count += 1
        
        # Normalize score
        grain_score = min(grain_count / 50.0, 1.0)
        return grain_score

    def analyze_soil_image(self, img: np.ndarray) -> Dict[str, float]:
        """
        Analyze soil image using traditional computer vision techniques
        Returns probability scores for different soil types
        """
        if img is None:
            raise ValueError("Invalid image data")

        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Initialize scores
        scores = {'Sandy': 0.0, 'Clay': 0.0, 'Loamy': 0.0}
        
        # 1. Color Analysis (based on HSV)
        avg_saturation = np.mean(hsv[:,:,1])
        avg_value = np.mean(hsv[:,:,2])
        
        # Color-based scoring
        sandy_color_score = min(avg_value / 255.0, 1.0) * 0.6  # Sandy is bright
        clay_color_score = min(avg_saturation / 255.0, 1.0) * (1.0 - (avg_value / 255.0 * 0.5))  # Clay is saturated and dark
        loamy_color_score = 1.0 - abs(avg_value/255.0 - 0.5) - abs(avg_saturation/255.0 - 0.5)  # Loamy is balanced
        loamy_color_score = max(0, loamy_color_score * 0.8)
        
        # 2. Texture Analysis
        texture_features = self.analyze_image_texture(gray)
        sandy_texture_score = texture_features['coarseness'] * 0.8
        clay_texture_score = (1.0 - texture_features['coarseness']) * 0.7
        loamy_texture_score = texture_features['homogeneity'] * 0.6
        
        # 3. Crack Detection (for clay)
        crack_score = self.detect_cracks(gray)
        clay_crack_score = crack_score * 0.9
        
        # 4. Grain/Granule Detection (for sandy)
        grain_score = self.detect_grains(gray)
        sandy_grain_score = grain_score * 0.8
        
        # Combine all scores with weights
        scores['Sandy'] = (
            sandy_color_score * 0.3 +
            sandy_texture_score * 0.4 +
            sandy_grain_score * 0.3
        )
        
        scores['Clay'] = (
            clay_color_score * 0.3 +
            clay_texture_score * 0.3 +
            clay_crack_score * 0.4
        )
        
        scores['Loamy'] = (
            loamy_color_score * 0.4 +
            loamy_texture_score * 0.4 +
            texture_features['homogeneity'] * 0.2
        )
        
        # Normalize scores to sum to 1
        total = sum(scores.values())
        if total > 0:
            for key in scores:
                scores[key] = scores[key] / total
        
        return scores

    # --- DECISION ENGINE ---
    def determine_soil_type(
        self,
        soil_scores: Dict[str, float],
        map_data: Dict,
        weather_data: Dict,
        location: Dict
    ) -> Dict:
        """Final decision engine combining all inputs"""
        
        # Extract data
        map_bias = map_data.get('soil_bias', {'Mixed': 1.0})
        weather_adjustments = weather_data.get('adjustments', {})
        
        # Apply weather adjustments
        adjusted_soil_scores = soil_scores.copy()
        
        if 'sandy_reduction' in weather_adjustments:
            reduction = weather_adjustments['sandy_reduction']
            adjusted_soil_scores['Sandy'] *= (1.0 - reduction)
        
        if 'clay_crack_increase' in weather_adjustments:
            increase = weather_adjustments['clay_crack_increase']
            adjusted_soil_scores['Clay'] *= (1.0 + increase)
        
        if 'texture_reliability' in weather_adjustments:
            reliability = weather_adjustments['texture_reliability']
            for soil_type in adjusted_soil_scores:
                adjusted_soil_scores[soil_type] *= reliability
        
        # Normalize soil scores
        total_soil = sum(adjusted_soil_scores.values())
        if total_soil > 0:
            for key in adjusted_soil_scores:
                adjusted_soil_scores[key] /= total_soil
        
        # Convert map bias
        map_bias_reliability = weather_adjustments.get('color_bias_reliability', 1.0)
        map_scores = self.convert_map_bias(map_bias, adjusted_soil_scores.keys())
        
        # Apply reliability to map scores
        for key in map_scores:
            map_scores[key] = map_scores[key] * map_bias_reliability + \
                             (1.0 - map_bias_reliability) * (1.0 / len(map_scores))
        
        # Normalize map scores
        total_map = sum(map_scores.values())
        if total_map > 0:
            for key in map_scores:
                map_scores[key] /= total_map
        
        # Combine scores with weights
        final_scores = {}
        for soil_type in adjusted_soil_scores.keys():
            final_scores[soil_type] = (
                0.5 * adjusted_soil_scores.get(soil_type, 0) +
                0.3 * map_scores.get(soil_type, 0) +
                0.2 * (1.0 / len(adjusted_soil_scores))
            )
        
        # Normalize final scores
        total_final = sum(final_scores.values())
        if total_final > 0:
            for key in final_scores:
                final_scores[key] /= total_final
        
        # Determine winning soil type
        soil_type = max(final_scores.items(), key=lambda x: x[1])
        
        # Generate reasons
        reasons = self.generate_reasons(
            soil_scores=soil_scores,
            map_data=map_data,
            weather_data=weather_data,
            final_scores=final_scores,
            winning_type=soil_type[0]
        )
        
        # Prepare result
        result = {
            'soil_type': soil_type[0],
            'confidence': round(soil_type[1], 2),
            'location': location,
            'map_color': map_data.get('average_color_rgb', (0, 0, 0)),
            'land_class': map_data.get('land_class', 'Unknown'),
            'final_scores': {k: round(v, 3) for k, v in final_scores.items()},
            'image_scores': {k: round(v, 3) for k, v in soil_scores.items()},
            'map_bias': {k: round(v, 3) for k, v in map_scores.items()},
            'weather_adjustments': weather_adjustments,
            'reason': reasons
        }
        
        return result
    
    def convert_map_bias(self, map_bias: Dict, target_soil_types: List[str]) -> Dict[str, float]:
        """Convert map bias to match available soil types"""
        converted = {soil_type: 0.0 for soil_type in target_soil_types}
        
        soil_type_mapping = {
            'Sandy': ['Sandy', 'SandyLoam', 'Gravel'],
            'Clay': ['Clay', 'ClayLoam'],
            'Loamy': ['Loamy', 'Loam', 'ClayLoam']
        }
        
        for map_soil, weight in map_bias.items():
            for target_soil, similar_types in soil_type_mapping.items():
                if map_soil in similar_types:
                    converted[target_soil] += weight / len(similar_types)
        
        return converted
    
    def generate_reasons(
        self,
        soil_scores: Dict,
        map_data: Dict,
        weather_data: Dict,
        final_scores: Dict,
        winning_type: str
    ) -> List[str]:
        """Generate human-readable reasons for the decision"""
        reasons = []
        
        # Image analysis reasons
        img_top = max(soil_scores.items(), key=lambda x: x[1])
        reasons.append(f"Image analysis suggests {img_top[0]} soil (score: {img_top[1]:.2f})")
        
        # Map-based reasons
        land_class = map_data.get('land_class', 'Unknown')
        reasons.append(f"Location classified as {land_class} based on satellite data")
        
        # Weather-based reasons
        adjustments = weather_data.get('adjustments', {})
        
        if adjustments.get('sandy_reduction', 0) > 0.1:
            reasons.append("Recent rainfall reduced sandy soil probability")
        
        if adjustments.get('clay_crack_increase', 0) > 0.1:
            reasons.append("High temperature increased clay cracking probability")
        
        if adjustments.get('texture_reliability', 1.0) < 0.8:
            reasons.append("High humidity reduced texture analysis reliability")
        
        # Final decision reason
        reasons.append(f"Combined analysis favors {winning_type} with highest confidence")
        
        return reasons

    # --- MAIN ENTRY POINT ---
    def process(self, image: np.ndarray, lat: float = None, lon: float = None) -> Dict:
        """Process a soil analysis request"""
        # 1. Analyze Image
        soil_scores = self.analyze_soil_image(image)
        
        # 2. Get Map Data (if lat/lon provided)
        map_data = self.get_land_info(lat, lon)
        
        # 3. Get Weather Data (if lat/lon provided)
        weather_data = self.get_weather_adjustments(lat, lon)
        
        # 4. Determine Soil Type
        result = self.determine_soil_type(
            soil_scores=soil_scores,
            map_data=map_data,
            weather_data=weather_data,
            location={'lat': lat, 'lon': lon}
        )
        
        return result
