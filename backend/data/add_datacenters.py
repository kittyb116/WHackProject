import pandas as pd
import json

def add_datacenter_info():
    """Add datacenter counts to models"""
    
    # Load models with speeds
    df = pd.read_csv('llm_models_with_speed.csv')
    
    # Load datacenter mapping
    with open('datacenters.json', 'r') as f:
        dc_data = json.load(f)
    
    datacenter_counts = dc_data['datacenter_counts']
    model_prefixes = dc_data['model_prefixes']
    
    def get_company(model_name):
        """Extract company from model name"""
        model_lower = model_name.lower()
        for prefix, company in model_prefixes.items():
            if prefix.lower() in model_lower:
                return company
        return "Unknown"
    
    def get_datacenter_count(company):
        """Get datacenter count for company"""
        return datacenter_counts.get(company, 5)
    
    # Add columns
    df['company'] = df['Model273/273'].apply(get_company)
    df['datacenter_count'] = df['company'].apply(get_datacenter_count)
    
    # Save
    df.to_csv('llm_models_with_features.csv', index=False)
    
    print(f"Added datacenter info to {len(df)} models")
    print(f"\nDatacenter Distribution:")
    print(df['datacenter_count'].value_counts().sort_index())
    print(f"\nCompany Distribution:")
    print(df['company'].value_counts())
    print(f"\nSample Data:")
    print(df[['Model273/273', 'company', 'datacenter_count', 'inference_speed_tokens_sec']].head(10))
    
    return df

if __name__ == "__main__":
    add_datacenter_info()