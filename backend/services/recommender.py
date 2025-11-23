import csv
import os
from typing import Dict, List, Tuple

# Load model data
MODELS_DATA = []
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data","llm_benchmark_scores.csv")

def load_models_data():
    """Load models from CSV file"""
    global MODELS_DATA
    if MODELS_DATA:  # Already loaded
        return MODELS_DATA
    
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        MODELS_DATA = list(reader)
    
    # Convert numeric fields
    for model in MODELS_DATA:
        model['Hard Prompts'] = int(model['Hard Prompts'])
        model['Coding'] = int(model['Coding'])
        model['Math'] = int(model['Math'])
        model['Creative Writing'] = int(model['Creative Writing'])
        model['Instruction Following'] = int(model['Instruction Following'])
        model['Longer Query'] = int(model['Longer Query'])
        model['Multi-Turn'] = int(model['Multi-Turn'])
        model['CO2_grams_per_query'] = float(model['CO2_grams_per_query'])
    
    return MODELS_DATA

# Category to CSV column mapping
CATEGORY_MAPPING = {
    "Hard Prompts": "Hard Prompts",
    "Coding": "Coding",
    "Math": "Math",
    "Creative Writing": "Creative Writing",
    "Instruction Following": "Instruction Following",
    "Longer Query": "Longer Query",
    "Multi-Turn": "Multi-Turn"
}

# GPT-4 baseline for comparison (chatgpt-4o-latest-2)
GPT4_BASELINE_CO2 = 4.32  # grams per query

def get_top_performers(category: str, top_n: int = 10) -> List[Dict]:
    """
    Get top N performing models for a given category
    Lower rank = better performance
    """
    models = load_models_data()
    column_name = CATEGORY_MAPPING[category]
    
    # Sort by category performance (lower is better)
    sorted_models = sorted(models, key=lambda x: x[column_name])
    
    return sorted_models[:top_n]

def calculate_savings(co2_used: float, baseline_co2: float = GPT4_BASELINE_CO2) -> Dict:
    """
    Calculate energy savings compared to baseline and generate comparison messages
    """
    savings = baseline_co2 - co2_used
    savings_percentage = (savings / baseline_co2) * 100 if baseline_co2 > 0 else 0
    
    # CO2 equivalents (approximate conversions)
    # Based on research: 1 email ≈ 4g CO2, 1 mile driving ≈ 404g CO2, 1 hour streaming ≈ 36g CO2
    emails_saved = savings / 4.0
    miles_saved = savings / 404.0
    streaming_minutes_saved = (savings / 36.0) * 60
    phone_charges_saved = savings / 8.0  # 1 phone charge ≈ 8g CO2
    
    # Generate messages
    comparison_messages = []
    
    if emails_saved >= 1:
        comparison_messages.append(f"💌 {abs(int(emails_saved))} emails worth of CO2")
    
    if miles_saved >= 0.01:
        comparison_messages.append(f"🚗 {abs(miles_saved):.2f} miles of driving")
    
    if streaming_minutes_saved >= 1:
        comparison_messages.append(f"📺 {abs(int(streaming_minutes_saved))} minutes of video streaming")
    
    if phone_charges_saved >= 0.1:
        comparison_messages.append(f"📱 {abs(phone_charges_saved):.1f} phone charges")
    
    # Main savings message
    if savings > 0:
        main_message = f"🌱 You saved {comparison_messages[0] if comparison_messages else f'{savings:.2f}g of CO2'}!"
    elif savings < 0:
        main_message = f"⚠️ This uses {comparison_messages[0] if comparison_messages else f'{abs(savings):.2f}g more CO2'} than GPT-4"
    else:
        main_message = "This model has similar emissions to GPT-4"
    
    return {
        "savings_grams": savings,
        "savings_percentage": savings_percentage,
        "main_message": main_message,
        "comparisons": comparison_messages
    }

# def get_recommendation(category: str) -> Dict:
#     """
#     Main recommendation logic:
#     1. Get top 10 performers in category
#     2. Sort by CO2, return top 3
#     """
#     # Get top performers
#     top_performers = get_top_performers(category, top_n=10)
    
#     if not top_performers:
#         raise ValueError(f"No models found for category: {category}")
    
#     # Sort by CO2 (lowest first)
#     top_performers_by_co2 = sorted(top_performers, key=lambda x: x['CO2_grams_per_query'])
    
#     # Get top 3 recommendations
#     recommendations = []
#     for i, model in enumerate(top_performers_by_co2[:3], 1):
#         savings_data = calculate_savings(model['CO2_grams_per_query'])
        
#         recommendations.append({
#             "rank": i,
#             "model": model['Model'],
#             "energy_cost": model['CO2_grams_per_query'],
#             "energy_saved": savings_data['savings_grams'],
#             "savings_message": savings_data['main_message'],
#             "comparison_messages": savings_data['comparisons'],
#             "performance_rank": model[CATEGORY_MAPPING[category]],
#             "model_details": {
#                 "co2_per_query": model['CO2_grams_per_query'],
#                 "source": model['Source'],
#                 "performance_scores": {
#                     "Hard Prompts": model['Hard Prompts'],
#                     "Coding": model['Coding'],
#                     "Math": model['Math'],
#                     "Creative Writing": model['Creative Writing'],
#                     "Instruction Following": model['Instruction Following'],
#                     "Longer Query": model['Longer Query'],
#                     "Multi-Turn": model['Multi-Turn']
#                 }
#             }
#         })
    
#     # Build response
#     response = {
#         "category": category,
#         "recommendations": recommendations,
#         "baseline_comparison": f"Compared to GPT-4 baseline ({GPT4_BASELINE_CO2}g CO2)"
#     }
    
#     return response

def get_recommendation(category: str) -> Dict:
    """
    Main recommendation logic:
    1. Get top 10 performers in category
    2. Sort by CO2, return top 3
    3. Use ONE consistent comparison unit for savings messages
    """
    # Get top performers
    top_performers = get_top_performers(category, top_n=10)
    
    if not top_performers:
        raise ValueError(f"No models found for category: {category}")
    
    # Sort by CO2 (lowest first)
    top_performers_by_co2 = sorted(top_performers, key=lambda x: x['CO2_grams_per_query'])
    
    # Determine which comparison to use (pick the most meaningful one from the best model)
    best_savings = GPT4_BASELINE_CO2 - top_performers_by_co2[0]['CO2_grams_per_query']

    # More realistic CO2 equivalents:
    # 1 Google search ≈ 1g CO2, 1 hour streaming ≈ 550g CO2
    # 1 mile driving ≈ 400g CO2, 1 minute LED bulb ≈ 0.007g CO2
    google_searches = best_savings / 1.0
    streaming_minutes = (best_savings / 550.0) * 60  # ~9g per minute
    miles = best_savings / 400.0
    led_minutes = best_savings / 0.007  # 10W LED bulb

    # Pick the most meaningful comparison (the largest value that's >= 1)
    if google_searches >= 1:
        comparison_type = "google_searches"
        unit = "Google searches"
        icon = "🔍"
    elif led_minutes >= 1:
        comparison_type = "led_minutes"
        unit = "minutes of LED light"
        icon = "💡"
    elif streaming_minutes >= 1:
        comparison_type = "streaming_minutes"
        unit = "minutes of video streaming"
        icon = "📺"
    elif miles >= 0.001:
        comparison_type = "miles"
        unit = "miles of driving"
        icon = "🚗"
    else:
        comparison_type = "grams"
        unit = "grams of CO2"
        icon = "🌱"
    
    # Get top 3 recommendations with CONSISTENT comparisons
    recommendations = []
    for i, model in enumerate(top_performers_by_co2[:3], 1):
        savings = GPT4_BASELINE_CO2 - model['CO2_grams_per_query']

        # Calculate ALL comparison types with realistic values
        google_searches_val = savings / 1.0
        streaming_minutes_val = (savings / 550.0) * 60
        miles_val = savings / 400.0
        led_minutes_val = savings / 0.007

        # Create savings message using the SAME unit for all 3
        if comparison_type == "google_searches":
            message_value = round(google_searches_val, 1)
        elif comparison_type == "led_minutes":
            message_value = round(led_minutes_val, 1)
        elif comparison_type == "streaming_minutes":
            message_value = round(streaming_minutes_val, 1)
        elif comparison_type == "miles":
            message_value = round(miles_val, 3)
        else:
            message_value = round(savings, 2)

        if savings > 0:
            savings_message = f"🌱 You saved {icon} {message_value} {unit}"
        elif savings < 0:
            savings_message = f"⚠️ Uses {icon} {abs(message_value)} more {unit} than GPT-4"
        else:
            savings_message = "Same emissions as GPT-4"

        recommendations.append({
            "rank": i,
            "model": model['Model'],
            "energy_cost": model['CO2_grams_per_query'],
            "energy_saved": savings,
            "energy_points": 10 if i == 1 else (5 if i == 2 else 3),  # XP points
            "savings_message": savings_message,
            "comparisons": {
                "google_searches": round(google_searches_val, 1),
                "miles": round(miles_val, 3),
                "streaming_minutes": round(streaming_minutes_val, 1),
                "led_minutes": round(led_minutes_val, 1)
            },
            "performance_rank": model[CATEGORY_MAPPING[category]],
            "source": model['Source']
        })
    
    # Build response
    response = {
        "category": category,
        "recommendations": recommendations,
        "baseline_comparison": f"All compared to GPT-4 baseline ({GPT4_BASELINE_CO2}g CO2)",
        "comparison_unit": unit
    }
    
    return response

def get_all_models() -> List[Dict]:
    """
    Returns all models with their complete data
    """
    return load_models_data()
