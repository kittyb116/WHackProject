import pickle
import pandas as pd
import os

def load_co2_model():
    """Load the trained XGBoost model"""
    model_path = '../models/energy_predictor.pkl'
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    return model

def predict_co2_emissions(inference_speed, datacenter_count):
    """
    Predict CO2 for ONE model at a time
    
    Use case: When you have a new/unknown model and want to estimate its CO2

    Args:
        inference_speed: tokens per second (e.g., 100)
        datacenter_count: number of datacenters (e.g., 40)
    
    Returns:
        float: predicted CO2 in grams per request
    """
    
    # Load trained model
    model = load_co2_model()
    
    # Create feature dataframe (must match training format)
    features = pd.DataFrame({
        'inference_speed_tokens_sec': [inference_speed],
        'datacenter_count': [datacenter_count]
    })
    
    # Make prediction
    co2_grams = model.predict(features)[0]
    
    return round(co2_grams, 3)

def predict_batch(models_df):
    """
    Predict CO2 for multiple models at once
    Use case: When you already have a DataFrame with multiple models

    Args:
        models_df: DataFrame with columns 'inference_speed_tokens_sec' and 'datacenter_count'
    
    Returns:
        array: predicted CO2 values
    """
    
    model = load_co2_model()
    
    features = models_df[['inference_speed_tokens_sec', 'datacenter_count']]
    predictions = model.predict(features)
    
    return predictions

# Example usage and testing
if __name__ == "__main__":
    print("Testing CO2 Prediction Model\n")
    print("=" * 60)


    
    # test_cases = [
    #     {
    #         'name': 'Fast model (Gemini Flash)',
    #         'speed': 185,
    #         'datacenters': 40
    #     },
    #     {
    #         'name': 'Slow reasoning model (O3)',
    #         'speed': 20,
    #         'datacenters': 10
    #     },
    #     {
    #         'name': 'Average model (GPT-4)',
    #         'speed': 60,
    #         'datacenters': 10
    #     },
    #     {
    #         'name': 'Fast small model (Claude Haiku)',
    #         'speed': 145,
    #         'datacenters': 5
    #     },
    #     {
    #         'name': 'Slow large model (Qwen3-235B)',
    #         'speed': 35,
    #         'datacenters': 27
    #     }
    # ]
    
    # for case in test_cases:
    #     co2 = predict_co2_emissions(case['speed'], case['datacenters'])
        
    #     print(f"\n{case['name']}:")
    #     print(f"  • Inference Speed: {case['speed']} tokens/sec")
    #     print(f"  • Datacenters: {case['datacenters']}")
    #     print(f"  • Predicted CO2: {co2}g per 100-token request")
        
    #     # Calculate equivalent comparisons
    #     emails_equivalent = round(co2 * 10)
    #     print(f"  • Equivalent to: ~{emails_equivalent} emails sent")
    
    # print("\n" + "=" * 60)
    # print("All predictions complete!")