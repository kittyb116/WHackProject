import os
import aiohttp
from typing import Literal

CategoryType = Literal["Hard Prompts", "Coding", "Math", "Creative Writing", "Instruction Following", "Longer Query", "Multi-Turn"]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

CLASSIFICATION_SYSTEM_PROMPT = """You are an expert at classifying user prompts into specific task categories for LLM usage.

Analyze the user's prompt and classify it into ONE of these 7 categories:

1. **Hard Prompts** - Complex, multi-step reasoning tasks requiring deep analysis
2. **Coding** - Programming, debugging, code generation, or technical implementation
3. **Math** - Mathematical problems, calculations, equations, or quantitative analysis
4. **Creative Writing** - Stories, poems, creative content, or imaginative writing
5. **Instruction Following** - Clear step-by-step instructions or procedural tasks
6. **Longer Query** - Extended research, comprehensive analysis, or detailed explanations
7. **Multi-Turn** - Conversational, back-and-forth dialogue requiring context awareness

CRITICAL RULES:
- Return ONLY the category name, nothing else
- Choose the SINGLE most appropriate category
- If multiple categories fit, prioritize in this order: Coding > Math > Hard Prompts > Creative Writing > Instruction Following > Longer Query > Multi-Turn
- DO NOT include any explanation, just the category name
- DO NOT use quotes or formatting

Examples:
User: "Write a Python function to sort a list"
Response: Coding

User: "Solve for x: 2x + 5 = 15"
Response: Math

User: "Write me a short story about a dragon"
Response: Creative Writing

User: "Explain quantum computing in detail with examples"
Response: Longer Query

Now classify this prompt:"""

async def classify_prompt(prompt: str) -> CategoryType:
    """
    Classifies a user prompt into one of 7 categories using Gemini 2.0 Flash
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Construct the full prompt for Gemini
    full_prompt = f"{CLASSIFICATION_SYSTEM_PROMPT}\n\nUser prompt: {prompt}"
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,  # Low temperature for consistent classification
            "maxOutputTokens": 50,
        }
    }
    
    # Make async request to Gemini API
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Gemini API error: {response.status} - {error_text}")
            
            data = await response.json()
            
            # Extract the category from Gemini's response
            try:
                category_raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Clean up the response (remove quotes, extra whitespace, etc.)
                category = category_raw.strip('"\'').strip()
                
                # Validate it's one of our categories
                valid_categories = [
                    "Hard Prompts", "Coding", "Math", "Creative Writing",
                    "Instruction Following", "Longer Query", "Multi-Turn"
                ]
                
                if category not in valid_categories:
                    # Fallback: try to match partial strings
                    category_lower = category.lower()
                    if "cod" in category_lower:
                        return "Coding"
                    elif "math" in category_lower:
                        return "Math"
                    elif "creat" in category_lower or "writ" in category_lower:
                        return "Creative Writing"
                    elif "instruct" in category_lower or "follow" in category_lower:
                        return "Instruction Following"
                    elif "long" in category_lower or "query" in category_lower:
                        return "Longer Query"
                    elif "multi" in category_lower or "turn" in category_lower:
                        return "Multi-Turn"
                    elif "hard" in category_lower or "complex" in category_lower:
                        return "Hard Prompts"
                    else:
                        # Default fallback
                        return "Instruction Following"
                
                return category
            
            except (KeyError, IndexError) as e:
                raise Exception(f"Failed to parse Gemini response: {str(e)}")