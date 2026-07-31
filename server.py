from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import json
from ingest import load_and_ingest
from sakhi_ai_agents import (
    run_pregnancy_knowledge_agent,
    run_government_scheme_agent,
    run_nutrition_agent
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load and ingest vector DB
    load_and_ingest("knowledge_base.json")
    print("Sakhi-AI API Server is ready.")
    yield

app = FastAPI(
    title="Sakhi-AI Knowledge Intelligence API",
    description="Autonomous Maternal Care Companion Backend",
    version="1.0.0",
    lifespan=lifespan
)

class PregnancyRequest(BaseModel):
    week: int

class SchemeRequest(BaseModel):
    age: int
    location: str
    week: int
    income_lpa: float

class NutritionRequest(BaseModel):
    week: int
    diet_type: str
    food_availability: str

@app.post("/api/v1/pregnancy-guidance")
async def get_pregnancy_guidance(req: PregnancyRequest):
    try:
        res = run_pregnancy_knowledge_agent(req.week)
        return json.loads(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scheme-recommendations")
async def get_scheme_recommendations(req: SchemeRequest):
    try:
        res = run_government_scheme_agent(req.age, req.location, req.week, req.income_lpa)
        return json.loads(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/nutrition-plan")
async def get_nutrition_plan(req: NutritionRequest):
    try:
        res = run_nutrition_agent(req.week, req.diet_type, req.food_availability)
        return json.loads(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)