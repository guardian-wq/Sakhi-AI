from firebase_setup import db

def get_pregnancy_week_info(week: int) -> dict:
    doc = db.collection("pregnancy_knowledge").document(f"week_{week}").get()
    return doc.to_dict() if doc.exists else {}

def query_eligible_schemes(user_age: int, user_income_lpa: float) -> list[dict]:
    query = db.collection("government_schemes").where("min_age", "<=", user_age).where("max_income_lpa", ">=", user_income_lpa)
    return [doc.to_dict() for doc in query.stream()]

def get_nutrition_guidance(trimester: int, diet_type: str) -> dict:
    doc = db.collection("nutrition_profiles").document(f"trimester_{trimester}_{diet_type.lower()}").get()
    return doc.to_dict() if doc.exists else {}