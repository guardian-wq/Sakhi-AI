from config import db

# 1. Save a sample mother profile
db.collection("mothers").document("mother_001").set({
    "name": "Priya",
    "pregnancy_week": 22,
    "status": "active"
})

print("✅ Data successfully sent to Firebase!")