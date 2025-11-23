import pandas as pd
from io import StringIO

def parse_manual_table():
    """Parse manually copied table HTML"""
    
    #fix so that file path works on all computers
    with open('/Users/kittyboakye/Documents/Wellesley/whack/WHackProject/backend/utils/table.html', 'r') as f:
        html_content = f.read()
    
    # Use pandas to parse the HTML table
    df_list = pd.read_html(StringIO(html_content))
    df = df_list[0]  # First table
    
    # Take top 50
    df = df.head(50)
    
    # Rename columns to match what we need
    # Adjust column names based on what you see
    df = df.rename(columns={
        'Model': 'Model',
        'Overall': 'Overall',
        # Add other column mappings
    })

     #fix so that file path works on all computers   
    df.to_csv('/Users/kittyboakye/Documents/Wellesley/whack/WHackProject/backend/data/llm_models_raw.csv', index=False)
    
    return(df)
