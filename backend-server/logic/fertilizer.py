def recommend_fertilizer_logic(crop: str, soil_type: str):
    recommendations = []
    
    crop = crop.lower()
    soil_type = soil_type.lower()
    
    # Example Logic
    if "clay" in soil_type:
        recommendations.append({"name": "Organic Compost", "desc": "Improves drainage and aeration in clay soil."})
        recommendations.append({"name": "Gypsum", "desc": "Helps break up compact clay."})
    elif "sandy" in soil_type:
        recommendations.append({"name": "Humus", "desc": "Increases water retention."})
        recommendations.append({"name": "NPK 10-10-10", "desc": "Balanced nutrients as sandy soil leaches quickly."})
    elif "loam" in soil_type:
         recommendations.append({"name": "Balanced Fertilizer", "desc": "Loam is ideal, just maintain nutrients."})
    elif "black" in soil_type: # Black Soil
         recommendations.append({"name": "Nitrogen", "desc": "Black soil is often rich, but may need N for leafy growth."})
    elif "red" in soil_type:
         recommendations.append({"name": "Phosphorus", "desc": "Red soil often lacks Phosphorus."})
         recommendations.append({"name": "Lime", "desc": "To correct acidity if present."})
    
    # Crop specific adjustments (simplified)
    if "wheat" in crop:
        recommendations.append({"name": "Urea", "desc": "Top dressing for nitrogen."})
    elif "rice" in crop:
        recommendations.append({"name": "DAP", "desc": "Basil application."})
    elif "corn" in crop:
        recommendations.append({"name": "Zinc Sulfate", "desc": "Corn is sensitive to Zinc deficiency."})

    # Default if no specific match
    if not recommendations:
        recommendations.append({"name": "General Purpose NPK", "desc": "Standard 17-17-17 fertilizer."})

    return recommendations
