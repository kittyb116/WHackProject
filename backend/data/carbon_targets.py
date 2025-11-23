import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle

def calculate_co2_emissions(total_evaluation_time_seconds):
    """
    Calculate CO2 emissions based on GPU power consumption
    Uses 8x H100 SXM GPUs benchmark from Virginia datacenter
    """
    if total_evaluation_time_seconds is None or total_evaluation_time_seconds <= 0:
        return -1

    # Power consumption for 8 H100 SXM GPUs in kilowatts (kW)
    power_consumption_kW = 5.6
    
    # Carbon intensity in grams CO₂ per kWh in Virginia
    carbon_intensity_g_per_kWh = 269.8
    
    # Convert evaluation time to hours
    total_evaluation_time_hours = total_evaluation_time_seconds / 3600
    
    # Calculate energy consumption in kWh
    energy_consumption_kWh = power_consumption_kW * total_evaluation_time_hours
    
    # Calculate CO₂ emissions in grams
    co2_emissions_g = energy_consumption_kWh * carbon_intensity_g_per_kWh
    
    # Return in grams (not kg)
    return co2_emissions_g

def create_co2_targets():
    """Create CO2 emission targets based on inference time calculation"""
    
    df = pd.read_csv('llm_models_with_features.csv')
    
    # Calculate inference time for a standard 100-token request
    # Formula: time = tokens / speed
    tokens_per_request = 100
    df['inference_time_seconds'] = tokens_per_request / df['inference_speed_tokens_sec']
    
    # Apply the CO2 calculation function to each model
    df['co2_grams_raw'] = df['inference_time_seconds'].apply(calculate_co2_emissions)
    
    # Adjust for datacenter efficiency
    # More datacenters = slight infrastructure overhead (1-5% increase)
    # This accounts for distributed infrastructure carbon footprint
    df['datacenter_efficiency_factor'] = 1 + (df['datacenter_count'] / 2000)
    
    df['co2_adjusted'] = df['co2_grams_raw'] * df['datacenter_efficiency_factor']
    
    # Add realistic variance (±10%) to account for:
    # - Different hardware configurations
    # - Network latency
    # - Datacenter PUE (Power Usage Effectiveness)
    # - Regional carbon intensity variations
    np.random.seed(42)
    variance = np.random.uniform(0.90, 1.10, len(df))
    df['co2_with_variance'] = df['co2_adjusted'] * variance
    
    # Use MinMaxScaler to ensure reasonable range
    # Real-world CO2 per 100-token request: 0.05g - 5.0g
    scaler = MinMaxScaler(feature_range=(0.05, 5.0))
    df['co2_grams_per_request'] = scaler.fit_transform(df[['co2_with_variance']])
    
    # Save scaler for later predictions on new models
    with open('../models/co2_scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    # Prepare final dataset
    output_cols = [
        'Model',
        'Overall',
        'company',
        'inference_speed_tokens_sec',
        'datacenter_count',
        'inference_time_seconds',
        'co2_grams_per_request'
    ]
    
    df_final = df[output_cols]
    df_final.to_csv('llm_models_training.csv', index=False)
    
    #co2 model statistics printed out
    print(f"Created CO2 targets for {len(df_final)} models")
    print(f"\nCO2 Emission Statistics:")
    print(df_final['co2_grams_per_request'].describe())
    
    print(f"\nInference Time Statistics:")
    print(df_final['inference_time_seconds'].describe())
    
    print(f"\nCorrelations:")
    corr_data = df_final[['inference_speed_tokens_sec', 'inference_time_seconds', 
                          'datacenter_count', 'co2_grams_per_request']]
    print(corr_data.corr()['co2_grams_per_request'].sort_values(ascending=False))
    
    print(f"\nTop 5 Most Efficient (Lowest CO2):")
    efficient = df_final.nsmallest(5, 'co2_grams_per_request')[
        ['Model', 'inference_speed_tokens_sec', 'inference_time_seconds', 'co2_grams_per_request']
    ]
    print(efficient.to_string(index=False))
    
    print(f"\n🔥 Top 5 Least Efficient (Highest CO2):")
    inefficient = df_final.nlargest(5, 'co2_grams_per_request')[
        ['Model', 'inference_speed_tokens_sec', 'inference_time_seconds', 'co2_grams_per_request']
    ]
    print(inefficient.to_string(index=False))
    
    # Show realistic CO2 values
    print(f"\n💡 Sample Real CO2 Calculations (before scaling):")
    print(f"   Fast model (200 tokens/sec, 0.5s inference): {calculate_co2_emissions(0.5):.6f}g")
    print(f"   Medium model (80 tokens/sec, 1.25s inference): {calculate_co2_emissions(1.25):.6f}g")
    print(f"   Slow model (30 tokens/sec, 3.33s inference): {calculate_co2_emissions(3.33):.6f}g")
    
    return df_final

if __name__ == "__main__":
    create_co2_targets()