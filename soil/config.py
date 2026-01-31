import os

class Config:
    # Map boundaries for Telangana
    LAT_TOP = 19.9178
    LAT_BOTTOM = 15.8361
    LON_LEFT = 77.2356
    LON_RIGHT = 81.3211
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Map file
    MAP_FILE = 'TS.png'
    
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
