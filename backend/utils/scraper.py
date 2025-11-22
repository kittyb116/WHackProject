import pandas as pd
from io import StringIO

def parse_manual_table():
    """Parse manually copied table HTML"""
    
    with open('table.html', 'r') as f:
        html_content = f.read()
    
    # Use pandas to parse the HTML table
    df_list = pd.read_html(StringIO(html_content))
    df = df_list[0]  # First table
    
    # Take top 50
    df = df.head(50)
    
    # Rename columns to match what we need
    # Adjust column names based on what you see
    df = df.rename(columns={
        'Model Name': 'Model',
        'Overall Score': 'Overall',
        # Add other column mappings
    })
    
    df.to_csv('backend/data/llm_models_raw.csv', index=False)
    print(f"✅ Parsed {len(df)} models from manual table")
    
    return df
