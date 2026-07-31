import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ai = genai.Client(api_key=GEMINI_API_KEY)

qdrant = QdrantClient(":memory:")
COLLECTION_NAME = "sakhi_ai_kb"

def setup_vector_db():
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )

def generate_embedding(text: str) -> list[float]:
    response = ai.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=768
        )
    )
    return response.embeddings[0].values

def load_and_ingest(json_path: str = "knowledge_base.json"):
    setup_vector_db()
    with open(json_path, 'r') as f:
        data = json.load(f)

    points = []
    idx = 1

    for item in data.get("pregnancy_weeks", []):
        text_content = f"Week {item['week']} Trimester {item['trimester']} Fetal: {item['fetal_development']} Maternal: {item['maternal_changes']} ANC: {item['anc_visit_milestone']}"
        vector = generate_embedding(text_content)
        points.append(PointStruct(
            id=idx,
            vector=vector,
            payload={"type": "pregnancy_week", "data": item, "search_text": text_content}
        ))
        idx += 1

    for scheme in data.get("schemes", []):
        text_content = f"Scheme: {scheme['scheme_name']}. Eligibility: {' '.join(scheme['eligibility_criteria'])}. Benefits: {scheme['benefits_description']}"
        vector = generate_embedding(text_content)
        points.append(PointStruct(
            id=idx,
            vector=vector,
            payload={"type": "government_scheme", "data": scheme, "search_text": text_content}
        ))
        idx += 1

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Sakhi-AI: Vector DB populated with {len(points)} knowledge embeddings.")

if __name__ == "__main__":
    load_and_ingest()