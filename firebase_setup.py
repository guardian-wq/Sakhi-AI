import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def seed_pregnancy_weeks():
    collection_ref = db.collection("pregnancy_knowledge")
    week_24_data = {
        "week": 24,
        "trimester": 2,
        "fetal_development": "Baby is around 1.3 pounds and 12 inches long. Taste buds are forming, lungs are developing branch structures.",
        "maternal_changes": "Uterine growth above navel, mild back aches, potential Braxton Hicks contractions, increased appetite.",
        "anc_visit_milestone": "Glucose Tolerance Test (GTT) screening for gestational diabetes, blood pressure check, fundal height measurement.",
        "warning_signs": [
            "Vaginal bleeding or fluid leaking",
            "Severe swelling in face/hands",
            "Persistent severe headache with visual disturbances",
            "Noticeable reduction in fetal movement"
        ],
        "lifestyle_recommendations": [
            "Sleep on the left side to optimize blood flow",
            "Perform light pelvic floor (Kegel) exercises",
            "Stay hydrated (2.5 to 3 liters of water daily)"
        ]
    }
    collection_ref.document(f"week_{week_24_data['week']}").set(week_24_data)
    print("Sakhi-AI: Successfully seeded 'pregnancy_knowledge' collection.")

def seed_government_schemes():
    collection_ref = db.collection("government_schemes")
    pmmvy = {
        "scheme_id": "pmmvy",
        "scheme_name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "min_age": 19,
        "max_income_lpa": 8.0,
        "state": "ALL",
        "target_trimester": [1, 2, 3],
        "eligibility_criteria": [
            "Pregnant women and lactating mothers for first and second child (if second child is female)",
            "Must not be in regular employment with Central/State Government or PSUs"
        ],
        "benefits_description": "Direct cash transfer of ₹5,000 in two installments upon fulfilling ANC and child vaccination milestones.",
        "financial_benefit_amount": 5000,
        "documents_required": [
            "Identity Proof (Government ID)",
            "Bank Account Details linked with NPCI/Aadhaar",
            "MCP Card (Mother and Child Protection Card)",
            "Pregnancy Registration Certificate"
        ],
        "application_steps": [
            "Register at local Anganwadi Centre (AWC) or ASHA worker unit within 150 days of LMP.",
            "Submit Form 1-A with MCP card details and bank account proof.",
            "Receive first installment upon pregnancy registration and minimum 1 ANC checkup."
        ]
    }
    collection_ref.document(pmmvy["scheme_id"]).set(pmmvy)
    print("Sakhi-AI: Successfully seeded 'government_schemes' collection.")

def seed_nutrition_profiles():
    collection_ref = db.collection("nutrition_profiles")
    nutrition_data = {
        "trimester": 2,
        "diet_type": "vegetarian",
        "key_nutrients": {
            "iron_mg": 27.0,
            "calcium_mg": 1000.0,
            "protein_g": 71.0,
            "folic_acid_mcg": 600.0
        },
        "recommended_foods": [
            "Lentils, chickpeas, and beans",
            "Spinach, fenugreek leaves (methi), and broccoli",
            "Milk, paneer, and yogurt",
            "Fortified cereals and whole grains"
        ],
        "foods_to_avoid": [
            "Unpasteurized dairy products",
            "Excessive caffeine (limit to <200mg/day)",
            "Raw or undercooked sprouts",
            "Unwashed raw vegetables"
        ]
    }
    collection_ref.document("trimester_2_vegetarian").set(nutrition_data)
    print("Sakhi-AI: Successfully seeded 'nutrition_profiles' collection.")

if __name__ == "__main__":
    seed_pregnancy_weeks()
    seed_government_schemes()
    seed_nutrition_profiles()