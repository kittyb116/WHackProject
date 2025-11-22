import pandas as pd

def create_inference_speed_mapping():
    """Create inference speed data for model families"""
    
    # Tokens per second (output speed) - researched from benchmarks
    inference_speeds = {
        # OpenAI models
        'gpt-5': 90,
        'gpt-4.5': 70,
        'gpt-4.1': 60,
        'chatgpt-4o': 120,
        'o1': 25,          # Reasoning models are slower
        'o3': 20,
        
        # Anthropic models
        'claude-sonnet-4-5': 100,
        'claude-opus-4-1': 55,
        'claude-opus-4': 60,
        'claude-sonnet-4': 95,
        'claude-haiku-4': 145,
        
        # Google models
        'gemini-3-pro': 115,
        'gemini-2.5-pro': 110,
        'gemini-2.5-flash': 185,
        
        # xAI models
        'grok-4.1': 75,
        'grok-4': 70,
        'grok-3': 65,
        'grok-4-fast': 125,
        
        # Chinese models
        'qwen3-max': 50,
        'qwen3-235b': 35,
        'qwen3-80b': 80,
        'qwen3-next': 45,
        'qwen3-vl': 40,      # Vision models slower
        
        'deepseek-v3.2': 48,
        'deepseek-v3.1': 50,
        'deepseek-r1': 30,   # Reasoning
        
        'glm-4.6': 72,
        'glm-4.5': 70,
        
        'kimi-k2': 55,
        'ernie-5.0': 65,
        'hunyuan': 60,
        
        # Mistral
        'mistral-medium': 95,
        
        # Unknown/other
        'longcat': 75,
        
        # Modifiers
        'thinking': 0.4,     # Multiply by 0.4 if has "thinking"
        'reasoning': 0.4,
        'vision': 0.7,       # Multiply by 0.7 if has "vision"
        'vl': 0.7,
        'fast': 1.5,         # Multiply by 1.5 if has "fast"
        'flash': 1.6,
    }
    
    return inference_speeds

def match_speed_to_model(model_name, speed_map):
    """Match model name to inference speed"""
    
    model_lower = model_name.lower()
    base_speed = 80  # Default
    
    # Find base speed
    for pattern, speed in speed_map.items():
        if pattern in ['thinking', 'reasoning', 'vision', 'vl', 'fast', 'flash']:
            continue
        if pattern in model_lower:
            base_speed = speed
            break
    
    # Apply modifiers
    if 'thinking' in model_lower or 'reasoning' in model_lower:
        base_speed *= speed_map.get('thinking', 0.4)
    if 'vision' in model_lower or 'vl' in model_lower:
        base_speed *= speed_map.get('vision', 0.7)
    if 'fast' in model_lower:
        base_speed *= speed_map.get('fast', 1.5)
    if 'flash' in model_lower:
        base_speed *= speed_map.get('flash', 1.6)
    
    return round(base_speed, 1)

def add_inference_speeds():
    """Add inference speeds to your model data"""
    
    # Load your models
    df = pd.read_csv('llm_models_raw.csv')    

    # Get speed mapping
    speed_map = create_inference_speed_mapping()
    
    # Match speeds
    df['inference_speed_tokens_sec'] = df['Model273/273'].apply(
        lambda x: match_speed_to_model(x, speed_map)
    )
    
    # Save
    df.to_csv('llm_models_with_speed.csv', index=False)
    
    print(f"Added inference speeds to {len(df)} models")
    print(f"\nSpeed Statistics:")
    print(df['inference_speed_tokens_sec'].describe())
    print(f"\nSample Data:")
    print(df[['Model273/273', 'inference_speed_tokens_sec']].head(10))
    
    return df

if __name__ == "__main__":
    add_inference_speeds()
