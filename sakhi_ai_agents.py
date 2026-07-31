import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ai = genai.Client(api_key=GEMINI_API_KEY)
qdrant = QdrantClient(":memory:")
COLLECTION_NAME = "sakhi_ai_kb"

def retrieve_context(query: str, limit: int = 3) -> list[dict]:
    response = ai.models.embed_content(
        model="gemini-embedding-001",  # Fixed model identifier
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=response.embedding.values,
        limit=limit
    )
    return [hit.payload for hit in hits]

# ==========================================
# 1. PREGNANCY KNOWLEDGE AGENT
# ==========================================

class PregnancyGuidanceResponse(BaseModel):
    trimester: int
    fetal_development: str
    mother_care_tips: list[str]
    anc_visit_info: str
    warning_signs: list[str]
    lifestyle_recommendations: list[str]

def run_pregnancy_knowledge_agent(week: int) -> str:
    kb_data = retrieve_context(f"Week {week} pregnancy development anc warning signs", limit=2)
    
    system_instruction = """
    You are Sakhi-AI's Autonomous Pregnancy Knowledge Companion. Provide concise, clinical, empathetic, 
    and structured maternal guidance based strictly on the provided context and week number.
    Always explicitly emphasize warning signs and red flags.
    """
    
    user_prompt = f"""
    Context: {json.dumps(kb_data)}
    User Query: Week {week} pregnancy guidance.
    Provide baby development details, mother care tips, ANC visit milestones, warning signs, and lifestyle advice.
    """

    response = ai.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=PregnancyGuidanceResponse,
            temperature=0.2,
        ),
    )
    return response.text

# ==========================================
# 2. GOVERNMENT SCHEME AGENT
# ==========================================

class SchemeRecommendation(BaseModel):
    scheme_name: str
    eligibility_status: str
    benefits: str
    documents_required: list[str]
    application_steps: list[str]

class SchemeAgentOutput(BaseModel):
    recommendations: list[SchemeRecommendation]

def run_government_scheme_agent(age: int, location: str, week: int, income_lpa: float) -> str:
    kb_data = retrieve_context("government maternity scheme cash assistance PMMVY JSY", limit=5)

    system_instruction = """
    You are Sakhi-AI's Government Scheme Advisor. Analyze the mother's profile against scheme requirements.
    Return eligible government schemes with benefits, documents required, and application procedures.
    Never output full government identity numbers (e.g., Aadhaar digits). Use standard placeholder document names.
    """

    user_prompt = f"""
    Scheme Context: {json.dumps(kb_data)}
    
    Mother Profile:
    - Age: {age}
    - Location: {location}
    - Pregnancy Week: {week}
    - Annual Income: {income_lpa} LPA
    
    Evaluate eligibility and return actionable schemes in JSON.
    """

    response = ai.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=SchemeAgentOutput,
            temperature=0.1,
        ),
    )
    return response.text

# ==========================================
# 3. NUTRITION AGENT
# ==========================================

class NutritionPlanResponse(BaseModel):
    daily_nutrition_plan: dict[str, str] = Field(description="Meal plan breakdown: breakfast, lunch, snack, dinner")
    key_protein_sources: list[str]
    key_iron_sources: list[str]
    key_calcium_sources: list[str]
    foods_to_avoid: list[str]

def run_nutrition_agent(week: int, diet_type: str, food_availability: str) -> str:
    system_instruction = """
    You are Sakhi-AI's Maternal Nutrition Specialist. Generate clear, practical, trimester-appropriate 
    nutrition recommendations based on user diet preferences and locally available food.
    """

    user_prompt = f"""
    User Input:
    - Pregnancy Week: {week}
    - Diet Preference: {diet_type}
    - Local Food Availability: {food_availability}

    Provide a balanced daily meal plan, key micronutrient sources (Iron, Calcium, Protein), and foods to avoid.
    """

    response = ai.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=NutritionPlanResponse,
            temperature=0.3,
        ),
    )
    return response.text