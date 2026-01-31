
import cv2
import numpy as np
import logging
from typing import Tuple, Dict
from config import Config

class MapReader:
    def __init__(self, map_path: str = Config.MAP_FILE):
        """Initialize map reader with the satellite map"""
        self.map_path = map_path
        self.map_image = cv2.imread(map_path)
        if self.map_image is None:
            # Create a dummy map for testing if file doesn't exist
            logging.warning(f"Map file {map_path} not found. Creating dummy map.")
            self._create_dummy_map()
        
        self.height, self.width = self.map_image.shape[:2]
        logging.info(f"Map loaded: {self.width}x{self.height}")
    
    def _create_dummy_map(self):
        """Create a dummy map for testing purposes"""
        # Create a 1000x1000 colored map for testing
        self.map_image = np.zeros((1000, 1000, 3), dtype=np.uint8)
        
        # Fill with different colored regions
        # Green - Forest
        self.map_image[0:400, 0:400] = [60, 160, 60]  # BGR format
        
        # Yellow - Crop Land
        self.map_image[0:400, 400:700] = [0, 200, 200]
        
        # Brown - Barren
        self.map_image[400:700, 0:400] = [30, 100, 180]
        
        # Pink - Scrub
        self.map_image[400:700, 400:700] = [200, 0, 200]
        
        # Blue - Water
        self.map_image[700:1000, 0:300] = [200, 100, 0]
        
        # Red - Urban
        self.map_image[700:1000, 300:1000] = [0, 0, 200]
    
    def gps_to_pixel(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert GPS coordinates to pixel coordinates in the map"""
        # Clamp coordinates to bounds
        lat_clamped = max(Config.LAT_BOTTOM, min(Config.LAT_TOP, lat))
        lon_clamped = max(Config.LON_LEFT, min(Config.LON_RIGHT, lon))
        
        # Calculate pixel coordinates
        x = int((lon_clamped - Config.LON_LEFT) / (Config.LON_RIGHT - Config.LON_LEFT) * self.width)
        y = int((Config.LAT_TOP - lat_clamped) / (Config.LAT_TOP - Config.LAT_BOTTOM) * self.height)
        
        # Clamp to image dimensions
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        return x, y
    
    def get_pixel_color_region(self, x: int, y: int, region_size: int = 7) -> Tuple[int, int, int]:
        """Get average color of a region around the pixel"""
        half_size = region_size // 2
        
        # Define region bounds
        x1 = max(0, x - half_size)
        x2 = min(self.width, x + half_size + 1)
        y1 = max(0, y - half_size)
        y2 = min(self.height, y + half_size + 1)
        
        # Extract region
        region = self.map_image[y1:y2, x1:x2]
        
        # Calculate average color (BGR format)
        avg_color = np.mean(region, axis=(0, 1))
        
        return tuple(map(int, avg_color))
    
    def classify_color(self, color: Tuple[int, int, int]) -> Dict:
        """Classify color into land class with tolerance"""
        b, g, r = color  # OpenCV uses BGR format
        
        for class_name, class_info in Config.COLOR_CLASSES.items():
            low_range, high_range = class_info['range']
            
            # Check if color is within tolerance range (RGB format)
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
