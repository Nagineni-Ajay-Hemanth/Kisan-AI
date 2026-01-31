
import cv2
import numpy as np
import os
from typing import Dict

class ImageAnalyzer:
    @staticmethod
    def analyze_soil_image(image_path: str) -> Dict[str, float]:
        """
        Analyze soil image using traditional computer vision techniques
        Returns probability scores for different soil types
        """
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Initialize scores
        scores = {'Sandy': 0.0, 'Clay': 0.0, 'Loamy': 0.0}
        
        # 1. Color Analysis (based on HSV)
        avg_hue = np.mean(hsv[:,:,0])
        avg_saturation = np.mean(hsv[:,:,1])
        avg_value = np.mean(hsv[:,:,2])
        
        # Color-based scoring
        sandy_color_score = min(avg_value / 255.0, 1.0) * 0.6  # Sandy is bright
        clay_color_score = min(avg_saturation / 255.0, 1.0) * (1.0 - (avg_value / 255.0 * 0.5))  # Clay is saturated and dark
        loamy_color_score = 1.0 - abs(avg_value/255.0 - 0.5) - abs(avg_saturation/255.0 - 0.5)  # Loamy is balanced
        loamy_color_score = max(0, loamy_color_score * 0.8)
        
        # 2. Texture Analysis
        texture_features = ImageAnalyzer._analyze_texture(gray)
        sandy_texture_score = texture_features['coarseness'] * 0.8
        clay_texture_score = (1.0 - texture_features['coarseness']) * 0.7
        loamy_texture_score = texture_features['homogeneity'] * 0.6
        
        # 3. Crack Detection (for clay)
        crack_score = ImageAnalyzer._detect_cracks(gray)
        clay_crack_score = crack_score * 0.9
        
        # 4. Grain/Granule Detection (for sandy)
        grain_score = ImageAnalyzer._detect_grains(gray)
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
    
    @staticmethod
    def _analyze_texture(gray_img: np.ndarray) -> Dict[str, float]:
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
    
    @staticmethod
    def _detect_cracks(gray_img: np.ndarray) -> float:
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
    
    @staticmethod
    def _detect_grains(gray_img: np.ndarray) -> float:
        """Detect sand grains using contour analysis"""
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray_img)
        
        # Threshold
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contour properties
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
