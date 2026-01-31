import cv2
import numpy as np
import sys
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from scipy import spatial
from sklearn.cluster import KMeans
import sqlite3


class AutoPlantDiseaseDetector:
    def __init__(self):
        """
        Advanced Plant Disease Detector with Automatic Crop Identification
        Detects both plant type and disease from leaf images
        """
        
        # Plant identification database - leaf characteristics
        self.plant_database = {
            'rice': {
                'common_name': 'Rice',
                'leaf_features': {
                    'shape': 'lanceolate',
                    'aspect_ratio': (6, 8),  # Length:Width ratio
                    'margin': 'entire',
                    'venation': 'parallel',
                    'color_hue_range': (35, 85),
                    'texture': 'smooth',
                    'size_category': 'medium'
                },
                'diseases': {
                    'blast': {
                        'type': 'fungal',
                        'symptoms': ['diamond_shaped_spots', 'white_gray_center', 'brown_border'],
                        'color_signature': ['gray_blight', 'necrosis_brown'],
                        'pattern': 'scattered_diamond_spots'
                    },
                    'bacterial_leaf_blight': {
                        'type': 'bacterial',
                        'symptoms': ['water_soaked_lesions', 'yellow_leaf_margin'],
                        'color_signature': ['water_soaked', 'yellowing'],
                        'pattern': 'linear_marginal'
                    },
                    'brown_spot': {
                        'type': 'fungal',
                        'symptoms': ['brown_oval_spots', 'yellow_halo'],
                        'color_signature': ['necrosis_brown', 'yellowing'],
                        'pattern': 'oval_spots_concentric'
                    }
                }
            },
            
            'wheat': {
                'common_name': 'Wheat',
                'leaf_features': {
                    'shape': 'linear',
                    'aspect_ratio': (10, 15),
                    'margin': 'entire',
                    'venation': 'parallel',
                    'color_hue_range': (40, 80),
                    'texture': 'ridged',
                    'size_category': 'narrow'
                },
                'diseases': {
                    'rust': {
                        'type': 'fungal',
                        'symptoms': ['orange_pustules', 'yellow_stripes'],
                        'color_signature': ['orange_rust', 'yellowing'],
                        'pattern': 'linear_stripes_pustules'
                    },
                    'powdery_mildew': {
                        'type': 'fungal',
                        'symptoms': ['white_powdery_patches'],
                        'color_signature': ['white_mildew'],
                        'pattern': 'powdery_coating'
                    }
                }
            },
            
            'tomato': {
                'common_name': 'Tomato',
                'leaf_features': {
                    'shape': 'compound_pinnate',
                    'aspect_ratio': (1.5, 2.5),
                    'margin': 'serrated',
                    'venation': 'pinnate',
                    'color_hue_range': (35, 75),
                    'texture': 'hairy',
                    'size_category': 'medium'
                },
                'diseases': {
                    'early_blight': {
                        'type': 'fungal',
                        'symptoms': ['bulls_eye_lesions', 'concentric_rings'],
                        'color_signature': ['necrosis_brown'],
                        'pattern': 'target_spots'
                    },
                    'late_blight': {
                        'type': 'fungal',
                        'symptoms': ['water_soaked_lesions', 'white_mold'],
                        'color_signature': ['water_soaked', 'white_mildew'],
                        'pattern': 'irregular_water_soaked'
                    },
                    'leaf_curl': {
                        'type': 'viral',
                        'symptoms': ['upward_curling', 'yellow_margins'],
                        'color_signature': ['yellowing'],
                        'pattern': 'curled_distorted'
                    }
                }
            },
            
            'brinjal': {
                'common_name': 'Brinjal (Eggplant)',
                'leaf_features': {
                    'shape': 'ovate',
                    'aspect_ratio': (1.2, 1.8),
                    'margin': 'entire_wavy',
                    'venation': 'pinnate',
                    'color_hue_range': (40, 85),
                    'texture': 'pubescent',
                    'size_category': 'large'
                },
                'diseases': {
                    'little_leaf': {
                        'type': 'phytoplasma',
                        'symptoms': ['small_leaves', 'bushy_appearance'],
                        'color_signature': ['yellowing'],
                        'pattern': 'stunted_small'
                    }
                }
            },
            
            'chilli': {
                'common_name': 'Chilli',
                'leaf_features': {
                    'shape': 'lanceolate',
                    'aspect_ratio': (2, 4),
                    'margin': 'entire',
                    'venation': 'pinnate',
                    'color_hue_range': (40, 80),
                    'texture': 'smooth',
                    'size_category': 'small'
                },
                'diseases': {
                    'anthracnose': {
                        'type': 'fungal',
                        'symptoms': ['sunken_lesions', 'black_fruiting_bodies'],
                        'color_signature': ['black_spots', 'necrosis_brown'],
                        'pattern': 'sunken_circular'
                    },
                    'leaf_curl': {
                        'type': 'viral',
                        'symptoms': ['upward_curling', 'thickened_leaves'],
                        'color_signature': ['yellowing'],
                        'pattern': 'curled_thick'
                    }
                }
            },
            
            'mustard': {
                'common_name': 'Mustard',
                'leaf_features': {
                    'shape': 'lyrate',
                    'aspect_ratio': (1, 1.5),
                    'margin': 'lobed',
                    'venation': 'reticulate',
                    'color_hue_range': (35, 70),
                    'texture': 'waxy',
                    'size_category': 'medium'
                },
                'diseases': {
                    'alternaria_blight': {
                        'type': 'fungal',
                        'symptoms': ['brown_black_spots', 'concentric_rings'],
                        'color_signature': ['necrosis_brown', 'black_spots'],
                        'pattern': 'concentric_rings'
                    },
                    'white_rust': {
                        'type': 'fungal',
                        'symptoms': ['white_pustules_underside'],
                        'color_signature': ['white_mildew'],
                        'pattern': 'clustered_pustules'
                    }
                }
            },
            
            'cotton': {
                'common_name': 'Cotton',
                'leaf_features': {
                    'shape': 'palmatifid',
                    'aspect_ratio': (1, 1.2),
                    'margin': 'lobed',
                    'venation': 'palmate',
                    'color_hue_range': (40, 75),
                    'texture': 'pubescent',
                    'size_category': 'large'
                },
                'diseases': {
                    'bacterial_blight': {
                        'type': 'bacterial',
                        'symptoms': ['angular_water_soaked', 'black_veins'],
                        'color_signature': ['water_soaked', 'black_spots'],
                        'pattern': 'angular_vein_limited'
                    }
                }
            },
            
            'maize': {
                'common_name': 'Maize',
                'leaf_features': {
                    'shape': 'lanceolate',
                    'aspect_ratio': (8, 12),
                    'margin': 'entire_wavy',
                    'venation': 'parallel',
                    'color_hue_range': (45, 85),
                    'texture': 'ridged',
                    'size_category': 'large'
                },
                'diseases': {
                    'leaf_blight': {
                        'type': 'fungal',
                        'symptoms': ['long_elliptical_lesions', 'gray_green_color'],
                        'color_signature': ['gray_blight', 'necrosis_brown'],
                        'pattern': 'elongated_lesions'
                    }
                }
            }
        }
        
        # Color ranges for disease detection (HSV)
        self.color_ranges = {
            'healthy_green': [
                {'lower': np.array([30, 40, 40]), 'upper': np.array([90, 255, 255])},
            ],
            'yellowing': [
                {'lower': np.array([20, 40, 100]), 'upper': np.array([35, 255, 255])},
            ],
            'necrosis_brown': [
                {'lower': np.array([0, 30, 20]), 'upper': np.array([20, 150, 100])},
                {'lower': np.array([0, 50, 0]), 'upper': np.array([180, 255, 60])}
            ],
            'orange_rust': [
                {'lower': np.array([5, 100, 100]), 'upper': np.array([20, 255, 255])},
            ],
            'white_mildew': [
                {'lower': np.array([0, 0, 150]), 'upper': np.array([180, 50, 255])},
            ],
            'black_spots': [
                {'lower': np.array([0, 0, 0]), 'upper': np.array([180, 255, 40])},
            ],
            'water_soaked': [
                {'lower': np.array([0, 0, 150]), 'upper': np.array([180, 50, 220])},
            ],
            'gray_blight': [
                {'lower': np.array([0, 0, 50]), 'upper': np.array([180, 30, 150])},
            ]
        }
        
        # Treatment database
        self.treatment_database = {
            'fungal': {
                'immediate': 'Apply appropriate fungicide based on disease',
                'preventive': 'Improve air circulation, avoid overhead watering',
                'organic': 'Neem oil 2-3%, copper-based fungicides',
                'chemical': 'Triazoles (tebuconazole), strobilurins (azoxystrobin)'
            },
            'bacterial': {
                'immediate': 'Copper-based bactericides, remove infected parts',
                'preventive': 'Use clean seeds/tools, crop rotation',
                'organic': 'Copper sprays, garlic extract',
                'chemical': 'Streptomycin, kasugamycin (where approved)'
            },
            'viral': {
                'immediate': 'Remove infected plants, control insect vectors',
                'preventive': 'Use virus-free planting material',
                'organic': 'Neem oil for vector control',
                'chemical': 'No cure, vector management only'
            }
        }
        
        print("Auto Plant Disease Detector Initialized")
        print(f"Can identify {len(self.plant_database)} plant types automatically")
        
        # Initialize extended database with 100+ new entries
        self._init_extended_database()
        
        # Initialize results database
        self._init_db()
        
        print(f"Extended database: Total {len(self.plant_database)} plant types")

    def _init_db(self):
        """Initialize SQLite database for storing results"""
        try:
            conn = sqlite3.connect('plant.db')
            cursor = conn.cursor()
            
            # Create detections table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_name TEXT,
                plant_detected TEXT,
                confidence REAL,
                primary_diagnosis TEXT,
                disease_details TEXT,
                health_status TEXT,
                visual_report_path TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization failed: {e}")

    def save_results_to_db(self, results):
        """Save analysis results to SQLite database"""
        try:
            conn = sqlite3.connect('plant.db')
            cursor = conn.cursor()
            
            # Extract basic info
            image_name = results.get('image', 'unknown')
            plant_info = results.get('plant_identification', {})
            plant_detected = plant_info.get('identified_as', 'unknown')
            confidence = plant_info.get('confidence', 0.0)
            
            # Extract disease info
            diseases = results.get('disease_diagnosis', [])
            if diseases:
                primary_diagnosis = diseases[0]['name']
                health_status = 'Diseased'
                if diseases[0]['type'] == 'healthy':
                    health_status = 'Healthy'
                elif diseases[0]['type'] == 'unknown':
                    health_status = 'Unknown'
            else:
                primary_diagnosis = "No Analysis"
                health_status = "Unknown"
            
            # Serialize full disease details
            disease_json = json.dumps(diseases)
            report_path = results.get('visual_report', '')
            
            # Insert
            cursor.execute('''
            INSERT INTO detections (
                image_name, plant_detected, confidence, 
                primary_diagnosis, disease_details, health_status, visual_report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_name, plant_detected, confidence,
                primary_diagnosis, disease_json, health_status, report_path
            ))
            
            conn.commit()
            conn.close()
            print(f"Results saved to database (ID: {cursor.lastrowid})")
            
        except Exception as e:
            print(f"Failed to save results to DB: {e}")

    def _init_extended_database(self):
        """Initialize massive extended database using templates"""
        
        # --- 1. Templates ---
        families = {
            'cucurbit': {'shape': 'palmate', 'aspect_ratio': (0.8, 1.2), 'margin': 'lobed', 'venation': 'palmate', 'texture': 'hairy', 'size_category': 'large', 'color_hue_range': (35, 75)},
            'citrus': {'shape': 'ovate', 'aspect_ratio': (1.5, 2.0), 'margin': 'entire', 'venation': 'pinnate', 'texture': 'waxy', 'size_category': 'medium', 'color_hue_range': (40, 80)},
            'fruit_tree': {'shape': 'ovate', 'aspect_ratio': (1.5, 2.5), 'margin': 'entire', 'venation': 'pinnate', 'texture': 'smooth', 'size_category': 'medium', 'color_hue_range': (35, 80)},
            'spice_herb': {'shape': 'lanceolate', 'aspect_ratio': (2.0, 4.0), 'margin': 'entire', 'venation': 'reticulate', 'texture': 'smooth', 'size_category': 'small', 'color_hue_range': (40, 85)},
            'spice_tree': {'shape': 'ovate', 'aspect_ratio': (1.8, 2.5), 'margin': 'entire', 'venation': 'pinnate', 'texture': 'leathery', 'size_category': 'large', 'color_hue_range': (30, 70)},
            'root_tuber': {'shape': 'lanceolate', 'aspect_ratio': (4.0, 8.0), 'margin': 'entire', 'venation': 'parallel', 'texture': 'smooth', 'size_category': 'large', 'color_hue_range': (40, 80)},
            'ornamental': {'shape': 'ovate', 'aspect_ratio': (1.2, 1.8), 'margin': 'serrated', 'venation': 'pinnate', 'texture': 'smooth', 'size_category': 'medium', 'color_hue_range': (30, 90)},
            'grass': {'shape': 'linear', 'aspect_ratio': (10, 20), 'margin': 'entire', 'venation': 'parallel', 'texture': 'rough', 'size_category': 'narrow', 'color_hue_range': (40, 85)},
            'palm': {'shape': 'pinnate_compound', 'aspect_ratio': (1, 1), 'margin': 'entire', 'venation': 'parallel', 'texture': 'fibrous', 'size_category': 'large', 'color_hue_range': (40, 80)},
            'leafy_herb': {'shape': 'ovate', 'aspect_ratio': (1.2, 1.5), 'margin': 'serrated', 'venation': 'reticulate', 'texture': 'soft', 'size_category': 'small', 'color_hue_range': (35, 80)},
            'generic_herb': {'shape': 'ovate', 'aspect_ratio': (1.2, 2.0), 'margin': 'serrated', 'venation': 'reticulate', 'texture': 'hairy', 'size_category': 'small', 'color_hue_range': (40, 80)},
        }

        # --- 2. Data (Name: (Family, [Diseases])) ---
        # User defined list 66-170
        data = {
            "Coriander (Leaves)": ("spice_herb", ["Powdery mildew", "Wilt", "Leaf spot", "Stem gall", "Root rot"]),
            "Mint": ("leafy_herb", ["Rust", "Leaf spot", "Powdery mildew", "Root rot", "Mosaic virus"]),
            "Cucumber": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Angular leaf spot"]),
            "Bottle Gourd": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Fruit rot"]),
            "Ridge Gourd": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Fruit rot"]),
            "Snake Gourd": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Fruit rot"]),
            "Bitter Gourd": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Fruit rot"]),
            "Pumpkin": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Fruit rot"]),
            "Ash Gourd": ("cucurbit", ["Downy mildew", "Powdery mildew", "Mosaic virus", "Anthracnose", "Fruit rot"]),
            "Drumstick": ("fruit_tree", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Twig blight"]),
            "Mango": ("fruit_tree", ["Anthracnose", "Powdery mildew", "Dieback", "Bacterial canker", "Malformation"]),
            "Banana": ("fruit_tree", ["Panama wilt", "Sigatoka leaf spot", "Bunchy top virus", "Anthracnose", "Crown rot"]),
            "Apple": ("fruit_tree", ["Scab", "Powdery mildew", "Fire blight", "Bitter rot", "Canker"]),
            "Orange": ("citrus", ["Citrus canker", "Greening (HLB)", "Tristeza virus", "Gummosis", "Scab"]),
            "Sweet Lime": ("citrus", ["Citrus canker", "Greening disease", "Tristeza virus", "Gummosis", "Leaf spot"]),
            "Lemon": ("citrus", ["Citrus canker", "Greening disease", "Scab", "Gummosis", "Tristeza virus"]),
            "Grapes": ("fruit_tree", ["Downy mildew", "Powdery mildew", "Anthracnose", "Botrytis bunch rot", "Leaf blight"]),
            "Guava": ("fruit_tree", ["Wilt", "Anthracnose", "Fruit rot", "Canker", "Leaf spot"]),
            "Papaya": ("fruit_tree", ["Ring spot virus", "Powdery mildew", "Anthracnose", "Root rot", "Leaf curl"]),
            "Pineapple": ("generic_herb", ["Heart rot", "Fruit rot", "Root rot", "Leaf spot", "Mealybug wilt"]),
            "Pomegranate": ("fruit_tree", ["Bacterial blight", "Anthracnose", "Fruit rot", "Wilt", "Leaf spot"]),
            "Watermelon": ("cucurbit", ["Downy mildew", "Powdery mildew", "Anthracnose", "Fusarium wilt", "Mosaic virus"]),
            "Muskmelon": ("cucurbit", ["Downy mildew", "Powdery mildew", "Fusarium wilt", "Anthracnose", "Mosaic virus"]),
            "Jackfruit": ("fruit_tree", ["Fruit rot", "Leaf spot", "Dieback", "Root rot", "Anthracnose"]),
            "Sapota": ("fruit_tree", ["Leaf spot", "Root rot", "Anthracnose", "Fruit rot", "Wilt"]),
            "Litchi": ("fruit_tree", ["Anthracnose", "Leaf blight", "Fruit rot", "Powdery mildew", "Dieback"]),
            "Peach": ("fruit_tree", ["Leaf curl", "Brown rot", "Powdery mildew", "Bacterial spot", "Canker"]),
            "Plum": ("fruit_tree", ["Brown rot", "Leaf curl", "Powdery mildew", "Bacterial spot", "Rust"]),
            "Pear": ("fruit_tree", ["Fire blight", "Scab", "Powdery mildew", "Leaf spot", "Canker"]),
            "Strawberry": ("generic_herb", ["Leaf spot", "Gray mold", "Powdery mildew", "Root rot", "Anthracnose"]),
            "Custard Apple": ("fruit_tree", ["Anthracnose", "Leaf spot", "Fruit rot", "Root rot", "Wilt"]),
            "Fig": ("fruit_tree", ["Rust", "Leaf spot", "Anthracnose", "Fruit rot", "Root rot"]),
            "Amla": ("fruit_tree", ["Rust", "Anthracnose", "Fruit rot", "Leaf spot", "Powdery mildew"]),
            "Jamun": ("fruit_tree", ["Anthracnose", "Leaf spot", "Fruit rot", "Wilt", "Dieback"]),
            "Dates": ("palm", ["Bayoud disease", "Leaf spot", "Root rot", "Fruit rot", "Black scorch"]),
            "Turmeric": ("root_tuber", ["Rhizome rot", "Leaf blotch", "Leaf spot", "Wilt", "Storage rot"]),
            "Ginger": ("root_tuber", ["Soft rot", "Bacterial wilt", "Leaf spot", "Fusarium wilt", "Rhizome rot"]),
            "Garlic": ("root_tuber", ["Purple blotch", "White rot", "Downy mildew", "Rust", "Basal rot"]),
            "Black Pepper": ("spice_herb", ["Quick wilt", "Pollu disease", "Anthracnose", "Leaf spot", "Slow decline"]),
            "Green Cardamom": ("root_tuber", ["Rhizome rot", "Leaf blight", "Capsule rot", "Mosaic virus", "Leaf streak"]),
            "Black Cardamom": ("root_tuber", ["Leaf blight", "Rhizome rot", "Wilt", "Leaf spot", "Capsule rot"]),
            "Clove": ("spice_tree", ["Leaf spot", "Dieback", "Wilt", "Anthracnose", "Root rot"]),
            "Cinnamon": ("spice_tree", ["Leaf spot", "Dieback", "Pink disease", "Root rot", "Wilt"]),
            "Nutmeg": ("spice_tree", ["Fruit rot", "Leaf spot", "Dieback", "Root rot", "Anthracnose"]),
            "Coriander (Seed)": ("spice_herb", ["Powdery mildew", "Stem gall", "Wilt", "Leaf spot", "Root rot"]),
            "Cumin": ("spice_herb", ["Wilt", "Blight", "Powdery mildew", "Root rot", "Alternaria leaf spot"]),
            "Fennel": ("spice_herb", ["Blight", "Powdery mildew", "Wilt", "Leaf spot", "Root rot"]),
            "Fenugreek": ("spice_herb", ["Powdery mildew", "Leaf spot", "Wilt", "Root rot", "Downy mildew"]),
            "Mustard Spice": ("spice_herb", ["Alternaria blight", "White rust", "Downy mildew", "Powdery mildew", "Sclerotinia rot"]),
            "Star Anise": ("spice_tree", ["Leaf spot", "Root rot", "Wilt", "Anthracnose", "Dieback"]),
            "Bay Leaf": ("spice_tree", ["Leaf spot", "Anthracnose", "Wilt", "Root rot", "Dieback"]),
            "Asafoetida": ("root_tuber", ["Root rot", "Wilt", "Leaf spot", "Collar rot", "Damping off"]),
            "Chilli Spice": ("spice_herb", ["Anthracnose", "Leaf curl virus", "Powdery mildew", "Wilt", "Mosaic virus"]),
            "Tea": ("spice_tree", ["Blister blight", "Red rust", "Brown blight", "Dieback", "Root rot"]),
            "Coffee": ("spice_tree", ["Coffee leaf rust", "Berry disease", "Wilt", "Root rot", "Cercospora leaf spot"]),
            "Rubber": ("fruit_tree", ["Abnormal leaf fall", "Powdery mildew", "Corynespora", "Pink disease", "Root rot"]),
            "Cocoa": ("fruit_tree", ["Black pod rot", "Witches broom", "Frosty pod rot", "Stem canker", "Leaf spot"]),
            "Coconut": ("palm", ["Bud rot", "Root wilt", "Leaf rot", "Stem bleeding", "Gray leaf blight"]),
            "Arecanut": ("palm", ["Fruit rot", "Bud rot", "Leaf spot", "Yellow leaf disease", "Root rot"]),
            "Cashew": ("fruit_tree", ["Anthracnose", "Powdery mildew", "Dieback", "Leaf spot", "Root rot"]),
            "Tobacco": ("generic_herb", ["Mosaic virus", "Black shank", "Downy mildew", "Leaf curl", "Root rot"]),
            "Tulsi": ("leafy_herb", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Mosaic virus"]),
            "Neem": ("fruit_tree", ["Leaf spot", "Powdery mildew", "Dieback", "Root rot", "Wilt"]),
            "Aloe Vera": ("generic_herb", ["Leaf rot", "Soft rot", "Anthracnose", "Leaf spot", "Root rot"]),
            "Ashwagandha": ("generic_herb", ["Leaf spot", "Root rot", "Wilt", "Damping off", "Powdery mildew"]),
            "Brahmi": ("leafy_herb", ["Leaf spot", "Root rot", "Wilt", "Damping off", "Powdery mildew"]),
            "Shatavari": ("root_tuber", ["Root rot", "Wilt", "Leaf spot", "Collar rot", "Damping off"]),
            "Giloy": ("generic_herb", ["Leaf spot", "Wilt", "Root rot", "Powdery mildew", "Anthracnose"]),
            "Lemongrass": ("grass", ["Leaf blight", "Rust", "Wilt", "Root rot", "Leaf spot"]),
            "Vetiver": ("grass", ["Leaf blight", "Root rot", "Wilt", "Leaf spot", "Rust"]),
            "Senna": ("generic_herb", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Anthracnose"]),
            "Isabgol": ("generic_herb", ["Downy mildew", "Leaf blight", "Root rot", "Wilt", "Powdery mildew"]),
            "Rose": ("ornamental", ["Black spot", "Powdery mildew", "Rust", "Dieback", "Botrytis blight"]),
            "Jasmine": ("ornamental", ["Leaf blight", "Rust", "Wilt", "Root rot", "Anthracnose"]),
            "Marigold": ("ornamental", ["Alternaria leaf spot", "Powdery mildew", "Wilt", "Root rot", "Leaf blight"]),
            "Lotus": ("generic_herb", ["Leaf blight", "Root rot", "Leaf spot", "Wilt", "Bacterial rot"]),
            "Lily": ("ornamental", ["Botrytis blight", "Leaf spot", "Root rot", "Mosaic virus", "Wilt"]),
            "Chrysanthemum": ("ornamental", ["Leaf blight", "Powdery mildew", "Wilt", "Rust", "Root rot"]),
            "Sunflower": ("ornamental", ["Alternaria leaf blight", "Rust", "Downy mildew", "Powdery mildew", "Root rot"]),
            "Orchid": ("ornamental", ["Leaf spot", "Root rot", "Crown rot", "Wilt", "Mosaic virus"]),
            "Tuberose": ("ornamental", ["Leaf blight", "Root rot", "Wilt", "Leaf spot", "Mosaic virus"]),
            "Hibiscus": ("ornamental", ["Leaf spot", "Powdery mildew", "Wilt", "Root rot", "Mosaic virus"]),
            "Bougainvillea": ("ornamental", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Dieback"]),
            "Teak": ("fruit_tree", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Dieback"]),
            "Sal": ("fruit_tree", ["Leaf blight", "Root rot", "Wilt", "Leaf spot", "Dieback"]),
            "Sandalwood": ("fruit_tree", ["Spike disease", "Leaf spot", "Root rot", "Wilt", "Dieback"]),
            "Bamboo": ("grass", ["Leaf blight", "Rust", "Root rot", "Wilt", "Leaf spot"]),
            "Eucalyptus": ("fruit_tree", ["Leaf blight", "Canker", "Root rot", "Wilt", "Rust"]),
            "Pine": ("fruit_tree", ["Needle blight", "Root rot", "Rust", "Wilt", "Canker"]),
            "Deodar": ("fruit_tree", ["Root rot", "Needle blight", "Wilt", "Canker", "Dieback"]),
            "Banyan": ("fruit_tree", ["Leaf spot", "Root rot", "Wilt", "Dieback", "Canker"]),
            "Peepal": ("fruit_tree", ["Leaf spot", "Root rot", "Wilt", "Powdery mildew", "Dieback"]),
            "Tamarind": ("fruit_tree", ["Powdery mildew", "Leaf spot", "Wilt", "Root rot", "Dieback"]),
            "Bael": ("fruit_tree", ["Leaf spot", "Root rot", "Wilt", "Powdery mildew", "Dieback"]),
            "Mahua": ("fruit_tree", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Dieback"]),
            "Berseem": ("grass", ["Leaf spot", "Powdery mildew", "Root rot", "Wilt", "Anthracnose"]),
            "Lucerne": ("grass", ["Leaf spot", "Wilt", "Root rot", "Downy mildew", "Powdery mildew"]),
            "Napier Grass": ("grass", ["Leaf blight", "Rust", "Wilt", "Root rot", "Leaf spot"]),
            "Guinea Grass": ("grass", ["Leaf blight", "Rust", "Root rot", "Wilt", "Leaf spot"]),
            "Fodder Maize": ("grass", ["Leaf blight", "Downy mildew", "Rust", "Root rot", "Mosaic virus"]),
            "Fodder Sorghum": ("grass", ["Downy mildew", "Leaf blight", "Rust", "Root rot", "Smut"]),
            "Fodder Cowpea": ("generic_herb", ["Mosaic virus", "Anthracnose", "Leaf spot", "Root rot", "Powdery mildew"]),
            "Betel Vine": ("cucurbit", ["Leaf rot", "Foot rot", "Powdery mildew", "Leaf spot", "Wilt"]),
            "Mushroom": ("generic_herb", ["Green mold", "Wet bubble", "Dry bubble", "Bacterial blotch", "Cobweb"]),
            "Organic Veg": ("generic_herb", ["Damping off", "Root rot", "Leaf spot", "Wilt", "Mosaic virus"]),
        }
        
        # --- 3. Build Database ---
        for plant, (family, disease_list) in data.items():
            base_feats = families.get(family, families['generic_herb']).copy()
            
            # Construct diseases
            plant_diseases = {}
            for d_name in disease_list:
                d_key = d_name.lower().replace(" ", "_")
                
                # Rule-based template matching
                if "mildew" in d_key and "downy" not in d_key:
                    symptoms = ['white_powdery_patches', 'leaf_distortion']
                    sig = ['white_mildew']
                    dtype = 'fungal'
                elif "downy" in d_key:
                    symptoms = ['yellow_patches', 'gray_fuzz_underside']
                    sig = ['yellowing', 'gray_blight']
                    dtype = 'fungal'
                elif "mosaic" in d_key or "virus" in d_key or "curl" in d_key:
                    symptoms = ['mottled_pattern', 'curled_leaves', 'stunting']
                    sig = ['yellowing']
                    dtype = 'viral'
                elif "wilt" in d_key or "rot" in d_key or "damping" in d_key:
                    symptoms = ['wilting', 'soft_decay', 'yellowing']
                    sig = ['necrosis_brown', 'yellowing']
                    dtype = 'fungal/bacterial'
                elif "rust" in d_key:
                    symptoms = ['orange_pustules', 'leaf_spots']
                    sig = ['orange_rust']
                    dtype = 'fungal'
                elif "anthracnose" in d_key or "blight" in d_key or "spot" in d_key:
                    symptoms = ['dark_lesions', 'concentric_rings']
                    sig = ['necrosis_brown', 'black_spots']
                    dtype = 'fungal'
                elif "bacterial" in d_key or "canker" in d_key:
                    symptoms = ['water_soaked_spots', 'yellow_halos']
                    sig = ['water_soaked']
                    dtype = 'bacterial'
                else:
                    symptoms = ['discoloration', 'lesions']
                    sig = ['necrosis_brown']
                    dtype = 'unknown'

                plant_diseases[d_key] = {
                    'type': dtype,
                    'symptoms': symptoms,
                    'color_signature': sig,
                    'pattern': 'variable'
                }
            
            self.plant_database[plant.lower().replace(" ", "_")] = {
                'common_name': plant,
                'leaf_features': base_feats,
                'diseases': plant_diseases
            }
    
    def preprocess_image(self, image):
        """Preprocess image for analysis"""
        # Resize
        height, width = image.shape[:2]
        max_dim = 800
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # Denoise
        image = cv2.GaussianBlur(image, (5, 5), 0)
        
        return image
    
    def segment_leaf(self, image):
        """Segment leaf from background using advanced techniques"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Method 1: Color-based segmentation
        green_mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        for color_range in self.color_ranges['healthy_green']:
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            green_mask = cv2.bitwise_or(green_mask, mask)
        
        # Method 2: GrabCut for refinement
        mask_gc = np.zeros(image.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        height, width = image.shape[:2]
        rect = (int(width*0.1), int(height*0.1), int(width*0.8), int(height*0.8))
        
        cv2.grabCut(image, mask_gc, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
        
        grabcut_mask = np.where((mask_gc == 2) | (mask_gc == 0), 0, 1).astype('uint8') * 255
        
        # Combine masks
        combined_mask = cv2.bitwise_or(green_mask, grabcut_mask)
        
        # Clean up
        kernel = np.ones((7,7), np.uint8)
        mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None, None
        
        # Get largest contour (main leaf)
        main_contour = max(contours, key=cv2.contourArea)
        
        # Create refined mask
        leaf_mask = np.zeros_like(mask)
        cv2.drawContours(leaf_mask, [main_contour], -1, 255, -1)
        
        return leaf_mask, main_contour, hsv
    
    def extract_shape_features(self, contour, image_shape):
        """Extract shape features for plant identification"""
        features = {}
        
        # Basic measurements
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / (h + 1e-5)
        features['aspect_ratio'] = aspect_ratio
        
        # Solidity (area / convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / (hull_area + 1e-5)
        features['solidity'] = solidity
        
        # Circularity
        circularity = (4 * np.pi * area) / (perimeter ** 2 + 1e-5)
        features['circularity'] = circularity
        
        # Extent (area / bounding rectangle area)
        rect_area = w * h
        extent = area / (rect_area + 1e-5)
        features['extent'] = extent
        
        # 1. Curl Index (Structural Gating)
        # Ratio of contour area to bounding box area.
        # Low fill ratio (high void space) indicates curling/distortion.
        features['curl_index'] = 1.0 - extent
        
        # Hu Moments (shape descriptors)
        moments = cv2.moments(contour)
        hu_moments = cv2.HuMoments(moments).flatten()
        
        # Log transform hu moments for better scale
        for i in range(7):
            features[f'hu_{i}'] = -1 * np.sign(hu_moments[i]) * np.log10(np.abs(hu_moments[i]) + 1e-10)
        
        # Ellipse fitting
        if len(contour) >= 5:
            ellipse = cv2.fitEllipse(contour)
            (center, axes, orientation) = ellipse
            major_axis = max(axes)
            minor_axis = min(axes)
            eccentricity = np.sqrt(1 - (minor_axis / (major_axis + 1e-5)) ** 2)
            features['eccentricity'] = eccentricity
            features['orientation'] = orientation
        else:
            features['eccentricity'] = 0
            features['orientation'] = 0
        
        # Compactness
        features['compactness'] = perimeter ** 2 / (4 * np.pi * area + 1e-5)
        
        # Relative size
        image_area = image_shape[0] * image_shape[1]
        features['relative_size'] = area / image_area
        
        return features
    
    def extract_texture_features(self, image, mask):
        """Extract texture features for plant identification"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        features = {}
        
        # Edge density
        edges = cv2.Canny(masked_gray, 50, 150)
        edge_pixels = cv2.countNonZero(edges)
        mask_pixels = cv2.countNonZero(mask)
        features['edge_density'] = edge_pixels / (mask_pixels + 1e-5)
        
        # Local Binary Patterns (simplified)
        lbp_features = self.compute_lbp(masked_gray, mask)
        features.update(lbp_features)
        
        # Color variation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv_masked = cv2.bitwise_and(hsv, hsv, mask=mask)
        
        h, s, v = cv2.split(hsv_masked)
        mask_indices = mask > 0
        
        if np.any(mask_indices):
            h_values = h[mask_indices]
            s_values = s[mask_indices]
            v_values = v[mask_indices]
            
            features['hue_mean'] = np.mean(h_values)
            features['hue_std'] = np.std(h_values)
            features['saturation_mean'] = np.mean(s_values)
            features['saturation_std'] = np.std(s_values)
            features['value_mean'] = np.mean(v_values)
            features['value_std'] = np.std(v_values)
        
        # GLCM-like features (simplified)
        glcm_features = self.compute_glcm_features(masked_gray)
        features.update(glcm_features)
        
        return features
    
    def compute_lbp(self, gray_image, mask):
        """Compute Local Binary Pattern features"""
        height, width = gray_image.shape
        lbp_image = np.zeros_like(gray_image)
        
        # Simple LBP
        for i in range(1, height-1):
            for j in range(1, width-1):
                if mask[i,j] == 0:
                    continue
                center = gray_image[i,j]
                code = 0
                code |= (gray_image[i-1,j-1] > center) << 7
                code |= (gray_image[i-1,j] > center) << 6
                code |= (gray_image[i-1,j+1] > center) << 5
                code |= (gray_image[i,j+1] > center) << 4
                code |= (gray_image[i+1,j+1] > center) << 3
                code |= (gray_image[i+1,j] > center) << 2
                code |= (gray_image[i+1,j-1] > center) << 1
                code |= (gray_image[i,j-1] > center) << 0
                lbp_image[i,j] = code
        
        # Histogram (within mask)
        hist = cv2.calcHist([lbp_image], [0], mask, [256], [0, 256])
        hist = hist / (np.sum(hist) + 1e-7)
        
        # Features from histogram
        return {
            'lbp_energy': np.sum(hist**2),
            'lbp_entropy': -np.sum(hist * np.log2(hist + 1e-7)),
            'lbp_uniformity': np.max(hist)
        }
    
    def compute_glcm_features(self, gray_image):
        """Compute simplified GLCM texture features"""
        # Simplified co-occurrence matrix for d=1, θ=0
        height, width = gray_image.shape
        co_matrix = np.zeros((256, 256))
        
        for i in range(height):
            for j in range(width-1):
                if gray_image[i,j] > 0 and gray_image[i,j+1] > 0:
                    val1 = min(int(gray_image[i,j]), 255)
                    val2 = min(int(gray_image[i,j+1]), 255)
                    co_matrix[val1, val2] += 1
        
        # Normalize
        if np.sum(co_matrix) > 0:
            co_matrix = co_matrix / np.sum(co_matrix)
        
        # Calculate features
        features = {}
        i, j = np.indices(co_matrix.shape)
        
        if np.any(co_matrix):
            # Contrast
            features['contrast'] = np.sum(co_matrix * (i - j) ** 2)
            
            # Homogeneity
            features['homogeneity'] = np.sum(co_matrix / (1 + (i - j) ** 2))
            
            # Energy
            features['energy'] = np.sum(co_matrix ** 2)
            
            # Correlation
            mean_i = np.sum(i * co_matrix)
            mean_j = np.sum(j * co_matrix)
            std_i = np.sqrt(np.sum(co_matrix * (i - mean_i) ** 2))
            std_j = np.sqrt(np.sum(co_matrix * (j - mean_j) ** 2))
            
            if std_i > 0 and std_j > 0:
                correlation = np.sum(co_matrix * (i - mean_i) * (j - mean_j)) / (std_i * std_j)
                features['correlation'] = correlation
            else:
                features['correlation'] = 0
        else:
            features['contrast'] = 0
            features['homogeneity'] = 0
            features['energy'] = 0
            features['correlation'] = 0
        
        return features
    
    def extract_color_features(self, hsv_image, mask):
        """
        Extract color features for disease detection.
        Includes HSV ranges and LAB color space for robust stress detection.
        """
        features = {}
        mask_pixels = cv2.countNonZero(mask)
        if mask_pixels == 0:
            return {}

        # --- 1. LAB Color Space Analysis (For Red/Purple Stress) ---
        # Convert HSV back to BGR, then to LAB to satisfy signature constraints
        # while still accessing the A-channel for red stress.
        bgr_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        lab_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
        
        # Mask the A-channel
        a_masked = cv2.bitwise_and(a_channel, a_channel, mask=mask)
        
        # In OpenCV LAB:
        # A-channel: 0-127 is Green-ish, 128-255 is Red/Magenta-ish
        # We look for pixels where A > 140 (Significant Red/Purple shift)
        red_stress_pixels = cv2.countNonZero(cv2.inRange(a_masked, 140, 255))
        features['red_index'] = red_stress_pixels / mask_pixels

        # --- 2. HSV Color Range Analysis ---
        for color_name, ranges in self.color_ranges.items():
            color_mask = np.zeros_like(mask)
            for color_range in ranges:
                range_mask = cv2.inRange(hsv_image, color_range['lower'], color_range['upper'])
                color_mask = cv2.bitwise_or(color_mask, range_mask)
            
            # Apply leaf mask
            color_mask = cv2.bitwise_and(color_mask, mask)
            color_pixels = cv2.countNonZero(color_mask)
            
            if mask_pixels > 0:
                features[color_name] = color_pixels / mask_pixels
            else:
                features[color_name] = 0
        
        # --- 3. Spot Detection (Brown/Black spots) ---
        # Combine necrosis_brown and black_spots if available
        spot_ratio = features.get('necrosis_brown', 0) + features.get('black_spots', 0)
        features['spot_index'] = spot_ratio
        
        # Note: Hue statistics purposefully removed to avoid interfering with disease logic
        return features
    
    def calculate_skewness(self, data):
        """Calculate skewness of data"""
        if len(data) < 3:
            return 0
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        skewness = np.mean(((data - mean) / std) ** 3)
        return skewness
    
    def identify_plant(self, shape_features, texture_features):
        """Identify plant type from extracted features"""
        scores = {}
        
        for plant_name, plant_info in self.plant_database.items():
            score = 0
            plant_feats = plant_info['leaf_features']
            
            # Aspect ratio matching
            target_ar_min, target_ar_max = plant_feats['aspect_ratio']
            actual_ar = shape_features.get('aspect_ratio', 1)
            
            if target_ar_min <= actual_ar <= target_ar_max:
                score += 2.0
            else:
                distance = min(abs(actual_ar - target_ar_min), abs(actual_ar - target_ar_max))
                score += max(0, 2.0 - distance)
            
            # Shape-based score aggregation
            # (Keeping existing logic but simplifying confidence output)
            expected_circularity = {
                'lanceolate': 0.3, 'linear': 0.2, 'compound_pinnate': 0.4,
                'ovate': 0.6, 'lyrate': 0.5, 'palmatifid': 0.7
            }.get(plant_feats['shape'], 0.5)
            
            score += 1.0 * (1 - abs(shape_features.get('circularity', 0) - expected_circularity))
            
            # Size matching
            relative_size = shape_features.get('relative_size', 0)
            if plant_feats['size_category'] == 'large' and relative_size > 0.4:
                score += 1.0
            elif plant_feats['size_category'] == 'small' and relative_size < 0.2:
                score += 1.0
            
            scores[plant_name] = score
        
        # Normalize scores
        max_possible = 6.0 # Approx max score
        max_score = 0
        top_plant = "unknown"
        
        if scores:
            top_plant = max(scores, key=scores.get)
            max_score = scores[top_plant]
            
        # Normalize all scores to 0-1 range for display
        for plant in scores:
            scores[plant] = min(scores[plant] / max_possible, 0.95)
        
        # 4. Fix Plant Identification Confidence Inflation
        # Normalize to 0-1 range but CAP at 0.85 to avoid overconfidence without ML
        confidence = min((max_score / max_possible), 0.85)
        
        return top_plant, confidence, dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3])
    
    def detect_diseases(self, plant_type, color_features, shape_features, texture_features):
        """
        Detect diseases using strict rule-based gating.
        Priority: Red Stress (Nutrient) > Viral (if Curled) > Fungal/Bacterial > Healthy
        """
        detected_diseases = []
        
        # Extract Key Metrics
        red_index = color_features.get('red_index', 0)
        spot_index = color_features.get('spot_index', 0)
        curl_index = shape_features.get('curl_index', 0)
        yellow_index = color_features.get('yellowing', 0)
        white_index = color_features.get('white_mildew', 0)
        water_soaked_index = color_features.get('water_soaked', 0)
        
        # --- RULE 1: LAB-Based Nutrient Deficiency (Red/Purple Stress) ---
        # "IF red_index > 0.15 AND spot_index < 0.1 AND curl_index < 0.25"
        if red_index > 0.15 and spot_index < 0.1 and curl_index < 0.25:
            detected_diseases.append({
                'name': 'Nutrient Deficiency (Phos/Potassium)',
                'type': 'nutritional',
                'confidence': 'High',
                'score': red_index,
                'symptoms': ['Purple/Red discoloration', 'No major spots', 'Stunted growth'],
                'original_symptoms': ['red_pigmentation', 'nutrient_stress']
            })
            return detected_diseases # Return immediately as this overrides others

        # --- RULE 2: Viral Disease (Structural Gating) ---
        # "Viral disease detection must be blocked unless curl_index > 0.25"
        if curl_index > 0.25:
            # Check for viral signs
            score = 0
            if yellow_index > 0.1: score += 0.4
            if texture_features.get('edge_density', 0) > 0.2: score += 0.3
            
            if score > 0.5:
                detected_diseases.append({
                    'name': 'Leaf Curl Virus',
                    'type': 'viral',
                    'confidence': 'High' if curl_index > 0.4 else 'Medium',
                    'score': curl_index,
                    'symptoms': ['Severe leaf curling', 'Distortion', 'Stunted growth'],
                    'original_symptoms': ['leaf_curl', 'mosaic']
                })
        
        # --- RULE 3: Fungal/Bacterial (Spot & Color Analysis) ---
        # Only check if we haven't found a major virus or stress issue yet
        if not detected_diseases:
            # Powdery Mildew
            if white_index > 0.15:
                detected_diseases.append({
                    'name': 'Powdery Mildew',
                    'type': 'fungal',
                    'confidence': 'High',
                    'score': white_index,
                    'symptoms': ['White powdery patches'],
                    'original_symptoms': ['powdery_mildew']
                })
            
            # Bacterial/Fungal Spots
            elif spot_index > 0.15 or water_soaked_index > 0.15:
                # Differentiate based on water-soaked look
                if water_soaked_index > spot_index:
                    name = 'Bacterial Blight'
                    type_ = 'bacterial'
                else:
                    name = 'Leaf Spot / Fungal Blight'
                    type_ = 'fungal'
                
                detected_diseases.append({
                    'name': name,
                    'type': type_,
                    'confidence': 'High' if spot_index > 0.25 else 'Medium',
                    'score': max(spot_index, water_soaked_index),
                    'symptoms': ['Dark lesions', 'Yellow halos'],
                    'original_symptoms': ['spots', 'lesions']
                })
            
            # Simple Yellowing (Nitrogen Deficiency) - Only if NOT viral/curled
            elif yellow_index > 0.25 and curl_index < 0.2:
                detected_diseases.append({
                    'name': 'Nitrogen Deficiency',
                    'type': 'nutritional',
                    'confidence': 'Medium',
                    'score': yellow_index,
                    'symptoms': ['General Yellowing (Chlorosis)'],
                    'original_symptoms': ['chlorosis']
                })

        # --- RULE 4: Default Conservative Diagnosis ---
        # "If no strong rule matches, output Early Stage Stress / Unclear"
        if not detected_diseases:
            if color_features.get('healthy_green', 0) > 0.6:
                detected_diseases.append({
                    'name': 'Healthy Plant',
                    'type': 'healthy',
                    'confidence': 'High',
                    'score': 0.9,
                    'symptoms': ['Normal green color', 'Good structural integrity'],
                    'original_symptoms': ['healthy']
                })
            else:
                detected_diseases.append({
                    'name': 'Early Stage Stress / Unclear',
                    'type': 'unknown',
                    'confidence': 'Low',
                    'score': 0.3,
                    'symptoms': ['Mild discoloration', 'No specific pattern detected'],
                    'original_symptoms': ['unclear_symptoms']
                })
        
        return detected_diseases[:1] # Return top diagnosis only for clarity
    
    def detect_generic_diseases(self, color_features):
        # Deprecated: Unified into detect_diseases with strict rules
        return []
    
    def get_treatment_recommendations(self, plant_type, diseases):
        """Get treatment recommendations based on plant and diseases"""
        recommendations = []
        
        if plant_type != "unknown":
            plant_name = self.plant_database[plant_type]['common_name']
            recommendations.append(f"\nPlant Identified: {plant_name}")
        else:
            recommendations.append("\nPlant: Unknown (Generic recommendations)")
        
        recommendations.append("\nDISEASE DIAGNOSIS & TREATMENT:")
        recommendations.append("=" * 50)
        
        for i, disease in enumerate(diseases, 1):
            recommendations.append(f"\n{i}. {disease['name']}")
            recommendations.append(f"   Type: {disease['type'].title()}")
            recommendations.append(f"   Confidence: {disease['confidence']}")
            
            # Get treatment based on disease type
            disease_type = disease['type']
            treatment = self.treatment_database.get(disease_type, {})
            
            if treatment:
                recommendations.append(f"\n   Recommended Treatment:")
                recommendations.append(f"   • Immediate: {treatment.get('immediate', 'Not specified')}")
                recommendations.append(f"   • Preventive: {treatment.get('preventive', 'Not specified')}")
                recommendations.append(f"   • Organic: {treatment.get('organic', 'Not specified')}")
                recommendations.append(f"   • Chemical: {treatment.get('chemical', 'Not specified')}")
            
            # Specific symptoms
            recommendations.append(f"\n   Symptoms detected:")
            for symptom in disease['symptoms'][:3]:
                recommendations.append(f"   • {symptom}")
        
        # General advice
        recommendations.append("\n" + "=" * 50)
        recommendations.append("\nGENERAL ADVICE:")
        recommendations.append("1. Isolate affected plants to prevent spread")
        recommendations.append("2. Remove severely infected leaves/plants")
        recommendations.append("3. Improve air circulation around plants")
        recommendations.append("4. Avoid overhead watering to keep leaves dry")
        recommendations.append("5. Maintain proper plant nutrition")
        recommendations.append("6. Monitor plants regularly for early detection")
        
        return "\n".join(recommendations)
    
    def generate_visualization(self, image, mask, contour, plant_name, diseases, output_path):
        """Generate visual report with annotations"""
        vis_img = image.copy()
        
        # Draw leaf contour
        cv2.drawContours(vis_img, [contour], -1, (0, 255, 0), 2)
        
        # Add plant identification
        cv2.putText(vis_img, f"Plant: {plant_name.title()}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Add disease information
        y_offset = 60
        cv2.putText(vis_img, "Disease Analysis:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        y_offset += 30
        for i, disease in enumerate(diseases[:3], 1):
            disease_text = f"{i}. {disease['name']} ({disease['confidence']})"
            color = (0, 0, 255) if disease['confidence'] == 'High' else \
                   (0, 165, 255) if disease['confidence'] == 'Medium' else \
                   (0, 255, 0)
            
            cv2.putText(vis_img, disease_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_offset += 25
        
        # Add severity indicators on leaf
        if diseases and diseases[0]['type'] != 'healthy':
            # Mark affected areas (simulated)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Highlight disease-colored areas
            for color_name in ['white_mildew', 'orange_rust', 'necrosis_brown', 'water_soaked']:
                if color_name in self.color_ranges:
                    for color_range in self.color_ranges[color_name]:
                        color_mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
                        color_mask = cv2.bitwise_and(color_mask, mask)
                        
                        # Create overlay
                        overlay = vis_img.copy()
                        overlay[color_mask > 0] = [0, 0, 255]  # Red for diseased areas
                        
                        # Blend
                        alpha = 0.3
                        vis_img = cv2.addWeighted(overlay, alpha, vis_img, 1 - alpha, 0)
        
        # Save visualization
        cv2.imwrite(output_path, vis_img)
        return output_path
    
    def analyze_leaf(self, image_path):
        """Main analysis function - automatic plant and disease detection"""
        print(f"\nAnalyzing: {os.path.basename(image_path)}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Could not load image"}
        
        # Preprocess
        img = self.preprocess_image(img)
        
        # Segment leaf
        mask, contour, hsv = self.segment_leaf(img)
        
        if mask is None:
            return {
                "status": "no_leaf",
                "message": "No leaf detected. Please ensure leaf is clearly visible."
            }
        
        # Extract features
        print("Extracting leaf features...")
        shape_features = self.extract_shape_features(contour, img.shape)
        
        # Note: texture/color extraction now needs the original BGR image for some conversions
        texture_features = self.extract_texture_features(img, mask)
        # Identify plant
        print("Identifying plant type...")
        plant_type, plant_confidence, plant_scores = self.identify_plant(shape_features, texture_features)
        
        # Force unknown if confidence is too low (Prevent bias)
        if plant_confidence < 0.4:
            plant_type = "unknown"
            print("Plant confidence low. Defaulting to 'unknown'.")
        
        # Detect diseases
        print("Detecting diseases...")
        # Note: We corrected extract_color_features to take only (hsv, mask)
        # Re-extracting cleanly here to be sure, although we could reuse existing 'hsv' var
        color_features = self.extract_color_features(hsv, mask) 
        
        diseases = self.detect_diseases(plant_type, color_features, shape_features, texture_features)
        
        # Generate visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vis_path = f"analysis_report_{timestamp}.jpg"
        self.generate_visualization(img, mask, contour, plant_type, diseases, vis_path)
        
        # Prepare comprehensive results
        results = {
            "status": "success",
            "image": os.path.basename(image_path),
            "plant_identification": {
                "identified_as": plant_type,
                "common_name": self.plant_database.get(plant_type, {}).get('common_name', 'Unknown'),
                "confidence": round(plant_confidence, 3),
                "top_candidates": plant_scores
            },
            "leaf_characteristics": {
                "size_ratio": round(shape_features.get('relative_size', 0), 3),
                "aspect_ratio": round(shape_features.get('aspect_ratio', 0), 2),
                "shape_features": {
                    "circularity": round(shape_features.get('circularity', 0), 3),
                    "eccentricity": round(shape_features.get('eccentricity', 0), 3),
                    "solidity": round(shape_features.get('solidity', 0), 3)
                },
                "texture_features": {
                    "edge_density": round(texture_features.get('edge_density', 0), 3),
                    "contrast": round(texture_features.get('contrast', 0), 3),
                    "homogeneity": round(texture_features.get('homogeneity', 0), 3)
                }
            },
            "color_analysis": {
                "healthy_green": round(color_features.get('healthy_green', 0), 3),
                "yellowing": round(color_features.get('yellowing', 0), 3),
                "disease_signatures": {k: round(v, 3) for k, v in color_features.items() 
                                      if k not in ['healthy_green', 'yellowing'] and v > 0.05}
            },
            "disease_diagnosis": diseases,
            "visual_report": vis_path,
            "treatment_recommendations": self.get_treatment_recommendations(plant_type, diseases)
        }
        
        # Save to database
        self.save_results_to_db(results)
        
        return results
    
    def batch_analyze(self, folder_path, output_json="batch_analysis.json"):
        """Analyze multiple images"""
        results = {}
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        for filename in os.listdir(folder_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_path = os.path.join(folder_path, filename)
                print(f"\nProcessing: {filename}")
                
                try:
                    result = self.analyze_leaf(image_path)
                    results[filename] = result
                except Exception as e:
                    results[filename] = {
                        "status": "error",
                        "message": str(e)
                    }
        
        # Save results
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nBatch analysis complete. Results saved to: {output_json}")
        return results


# --- Main Execution ---
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automatic Plant & Disease Detector - No Crop Input Needed",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image leaf.jpg
  %(prog)s --folder ./plant_images
  %(prog)s --demo  (for demonstration)
        """
    )
    
    parser.add_argument("--image", type=str, help="Path to leaf image")
    parser.add_argument("--folder", type=str, help="Path to folder with multiple leaf images")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--output", type=str, default="plant_analysis.json", 
                       help="Output JSON file")
    
    args = parser.parse_args()
    
    detector = AutoPlantDiseaseDetector()
    
    if args.demo:
        print("\n" + "="*70)
        print("AUTOMATIC PLANT & DISEASE DETECTION DEMONSTRATION")
        print("="*70)
        
        # Create demo image
        demo_img = create_demo_leaf()
        demo_path = "demo_leaf.jpg"
        cv2.imwrite(demo_path, demo_img)
        print(f"\nCreated demo leaf image: {demo_path}")
        
        results = detector.analyze_leaf(demo_path)
        
        # Display results
        print("\n" + "="*50)
        print("DEMO RESULTS:")
        print("="*50)
        display_results(results)
        
        # Cleanup
        if os.path.exists(demo_path):
            os.remove(demo_path)
        
        print(f"\nDemo completed. Real images will provide more accurate results.")
    
    elif args.image:
        if os.path.exists(args.image):
            results = detector.analyze_leaf(args.image)
            
            # Save results
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Display results
            display_results(results)
            print(f"\nDetailed results saved to: {args.output}")
            print(f"Visual report: {results.get('visual_report', 'Not generated')}")
        
        else:
            print(f"Error: Image not found: {args.image}")
    
    elif args.folder:
        if os.path.exists(args.folder):
            print(f"Analyzing all leaf images in: {args.folder}")
            results = detector.batch_analyze(args.folder, args.output)
            print(f"Batch analysis complete. Results saved to: {args.output}")
        else:
            print(f"Error: Folder not found: {args.folder}")
    
    else:
        # Interactive mode
        print("\n" + "="*70)
        print("AUTOMATIC PLANT & DISEASE DETECTOR")
        print("="*70)
        print("\nSimply provide a leaf image. No need to specify plant type!")
        
        image_path = input("\nEnter path to leaf image: ").strip()
        
        # Remove quotes if present
        if image_path.startswith(('"', "'")) and image_path.endswith(('"', "'")):
            image_path = image_path[1:-1]
        
        if os.path.exists(image_path):
            print("\nAnalyzing image...")
            results = detector.analyze_leaf(image_path)
            display_results(results)
            
            # Ask to save results
            save = input("\nSave results to file? (y/n): ").lower()
            if save == 'y':
                filename = input("Enter filename (default: plant_analysis.json): ").strip()
                if not filename:
                    filename = "plant_analysis.json"
                
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"Results saved to: {filename}")
        
        else:
            print(f"\nError: File not found: {image_path}")


def display_results(results):
    """Display analysis results in readable format"""
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    if results.get("status") != "success":
        print(f"Status: {results.get('status', 'unknown')}")
        print(f"Message: {results.get('message', 'No message')}")
        return
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print("="*60)
    
    # Plant identification
    plant_info = results["plant_identification"]
    print(f"\n🌿 PLANT IDENTIFICATION:")
    print(f"   Identified as: {plant_info['common_name']}")
    print(f"   Confidence: {plant_info['confidence']:.1%}")
    
    if plant_info['top_candidates']:
        print(f"   Other possibilities:")
        for plant, score in list(plant_info['top_candidates'].items())[1:3]:
            print(f"     • {plant.title()}: {score:.1%}")
    
    # Leaf characteristics
    leaf_info = results["leaf_characteristics"]
    print(f"\n🍃 LEAF CHARACTERISTICS:")
    print(f"   Size ratio: {leaf_info['size_ratio']:.1%} of image")
    print(f"   Aspect ratio: {leaf_info['aspect_ratio']:.2f}")
    print(f"   Shape: {'Elongated' if leaf_info['shape_features']['eccentricity'] > 0.7 else 'Broad'}")
    
    # Disease diagnosis
    diseases = results["disease_diagnosis"]
    print(f"\n⚠️  DISEASE DIAGNOSIS:")
    
    if diseases and diseases[0]['name'] != 'Healthy Plant':
        for disease in diseases:
            print(f"\n   {disease['name']} ({disease['type'].upper()})")
            print(f"   Confidence: {disease['confidence']}")
            print(f"   Symptoms detected:")
            for symptom in disease['symptoms'][:3]:
                print(f"     • {symptom}")
    else:
        print("   ✅ Plant appears healthy!")
        if diseases:
            for symptom in diseases[0]['symptoms'][:2]:
                print(f"     • {symptom}")
    
    # Color analysis
    color_info = results["color_analysis"]
    print(f"\n🎨 COLOR ANALYSIS:")
    print(f"   Healthy green: {color_info['healthy_green']:.1%}")
    
    if color_info['disease_signatures']:
        print(f"   Disease indicators:")
        for color, value in color_info['disease_signatures'].items():
            if value > 0.05:
                print(f"     • {color.replace('_', ' ')}: {value:.1%}")
    
    # Quick recommendations
    if diseases and diseases[0]['name'] != 'Healthy Plant':
        primary_disease = diseases[0]
        print(f"\n💡 QUICK ACTION:")
        
        if primary_disease['type'] == 'fungal':
            print("   Apply fungicide spray")
            print("   Improve air circulation")
        elif primary_disease['type'] == 'bacterial':
            print("   Remove infected leaves")
            print("   Apply copper-based spray")
        elif primary_disease['type'] == 'viral':
            print("   Remove infected plants")
            print("   Control insect vectors")
        
        print(f"\n   Full treatment recommendations in saved report")


def create_demo_leaf():
    """Create a demo leaf image for testing"""
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Draw tomato-like leaf (compound shape)
    center = (400, 300)
    
    # Main leaflet
    cv2.ellipse(img, center, (150, 80), 30, 0, 360, (34, 139, 34), -1)
    
    # Smaller leaflets
    for angle in [60, 0, -60]:
        offset_x = int(100 * np.cos(np.radians(angle)))
        offset_y = int(100 * np.sin(np.radians(angle)))
        cv2.ellipse(img, (center[0]+offset_x, center[1]+offset_y), 
                   (60, 40), angle, 0, 360, (50, 150, 50), -1)
    
    # Add some disease symptoms (early blight)
    for i in range(4):
        spot_x = np.random.randint(300, 500)
        spot_y = np.random.randint(200, 400)
        radius = np.random.randint(15, 30)
        
        # Brown spots with concentric rings
        cv2.circle(img, (spot_x, spot_y), radius, (42, 42, 165), -1)  # Brown
        cv2.circle(img, (spot_x, spot_y), radius//2, (255, 255, 255), 2)  # White ring
    
    # Add texture
    noise = np.random.normal(0, 8, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)
    
    return img


if __name__ == "__main__":
    main()