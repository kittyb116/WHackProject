from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from services.classifier import classify_prompt
from services.recommender import get_recommendation
import uvicorn

app = FastAPI(
    title="LLM Energy-Efficient Recommendation API",
    description="Recommends the most energy-efficient LLM for a given task",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class RecommendationResponse(BaseModel):
    # model_config = {"protected_namespaces": ()}  # Add this line
    
    # category: str
    # recommended_model: str
    # energy_cost: float
    # energy_saved: float
    # savings_message: str
    # comparison_messages: List[str]
    # model_details: Dict
    # alternatives: List[Dict]
    model_config = {"protected_namespaces": ()}
    
    category: str
    recommendations: List[Dict]  # Changed from single model to list
    # baseline_model: str
    # baseline_cost: float
    baseline_comparison: str


class SingleRecommendation(BaseModel):
    rank: int
    model: str
    energy_cost: float
    energy_saved: float
    savings_message: str
    comparison_messages: List[str]
    performance_rank: int
@app.get("/")
async def root():
    return {
        "message": "LLM Energy-Efficient Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "/recommend": "POST - Get model recommendation for a prompt",
            "/models": "GET - List all available models",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_model(request: PromptRequest):
    """
    Main endpoint: Takes a user prompt and returns the best energy-efficient model recommendation
    """
    try:
        if not request.prompt or len(request.prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        print(f"DEBUG: Received prompt: {request.prompt}")
        
        # Step 1: Classify the prompt using Gemini
        category = await classify_prompt(request.prompt)
        print(f"DEBUG: Classified as: {category}")
        
        # Step 2: Get recommendation based on category
        recommendation = get_recommendation(category)
        # print(f"DEBUG: Recommendation: {recommendation['recommended_model']}")
        
        return recommendation
    
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"Error processing recommendation: {str(e)}")

@app.get("/models")
async def list_models():
    """
    Returns all available models with their stats
    """
    from recommender import get_all_models
    return get_all_models()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)