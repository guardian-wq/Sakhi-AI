import os
from dotenv import load_dotenv  # Add this
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()  # Add this line to load GEMINI_API_KEY from .env

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-key.json"))
firebase_admin.initialize_app(cred, {
        'projectId': os.getenv("FIREBASE_PROJECT_ID", "sakhi-ai-92eb9")
    })

db = firestore.client()