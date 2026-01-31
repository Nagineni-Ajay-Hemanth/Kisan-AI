
from typing import Dict, List
from config import Config

class DecisionEngine:
    @staticmethod
    def determine_soil_type(
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
        map_scores = DecisionEngine._convert_map_bias(map_bias, adjusted_soil_scores.keys())
        
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
        reasons = DecisionEngine._generate_reasons(
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
    
    @staticmethod
    def _convert_map_bias(map_bias: Dict, target_soil_types: List[str]) -> Dict[str, float]:
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
    
    @staticmethod
    def _generate_reasons(
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
