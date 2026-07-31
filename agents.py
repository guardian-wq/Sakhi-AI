import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from google import genai
from google.genai import types
from PIL import Image
from config import db

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"


class DocumentIntelligenceAgent:
    @staticmethod
    def process_document_image(image_path: str) -> Dict[str, Any]:
        image = Image.open(image_path)
        prompt = """
        You are a healthcare document processing assistant for rural mothers.
        Analyze the provided image (Pregnancy certificate, Bank details, or Identity card).
        
        Extract the following information in strict JSON format:
        {
            "name": string or null,
            "pregnancy_status": "verified" | "unverified" | "unclear",
            "expected_delivery_date": "YYYY-MM-DD" or null,
            "document_type": "Pregnancy certificate" | "Identity Document" | "Bank details" | "Unknown",
            "unclear_image_detected": boolean,
            "missing_fields": list of strings
        }
        RULES:
        1. If the image is blurry, set "unclear_image_detected": true.
        2. Never return sensitive government identification digits.
        """
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[image, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse document content", "unclear_image_detected": True}

    @staticmethod
    def save_verified_document_data(mother_id: str, extracted_data: Dict[str, Any]) -> None:
        doc_ref = db.collection("mothers").document(mother_id)
        update_payload = {
            f"documents.{extracted_data.get('document_type', 'unknown').lower()}": True,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        if extracted_data.get("name"):
            update_payload["name"] = extracted_data["name"]
        if extracted_data.get("expected_delivery_date"):
            update_payload["edd"] = extracted_data["expected_delivery_date"]
            
        doc_ref.set(update_payload, merge=True)


class MemoryAgent:
    @staticmethod
    def get_profile(mother_id: str) -> Dict[str, Any]:
        doc = db.collection("mothers").document(mother_id).get()
        return doc.to_dict() if doc.exists else {}

    @staticmethod
    def save_chat_turn(mother_id: str, role: str, content: str) -> None:
        db.collection("conversation_memory").document(mother_id)\
          .collection("messages").add({
              "role": role,
              "content": content,
              "timestamp": datetime.now(timezone.utc)
          })

    @staticmethod
    def get_recent_history(mother_id: str, limit: int = 5) -> List[Dict[str, str]]:
        docs = db.collection("conversation_memory").document(mother_id)\
                 .collection("messages")\
                 .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                 .limit(limit).stream()
        messages = [{"role": d.get("role"), "content": d.get("content")} for d in docs]
        return messages[::-1]

    @staticmethod
    def contextual_chat(mother_id: str, user_query: str) -> str:
        profile = MemoryAgent.get_profile(mother_id)
        history = MemoryAgent.get_recent_history(mother_id)

        system_instruction = f"""
        You are Sakhi-AI, an empathetic, knowledgeable maternal care assistant dedicated to helping rural mothers.
        User Profile Context:
        - Name: {profile.get('name', 'Mother')}
        - Pregnancy Week: {profile.get('pregnancy_week', 'Unknown')}
        - EDD: {profile.get('edd', 'Unknown')}
        - Location: {profile.get('location', 'Unknown')}
        
        Always address the user warmly using their name and relevant context when appropriate.
        """

        formatted_contents = [f"{h['role'].upper()}: {h['content']}" for h in history]
        formatted_contents.append(f"USER: {user_query}")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="\n".join(formatted_contents),
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )

        MemoryAgent.save_chat_turn(mother_id, "user", user_query)
        MemoryAgent.save_chat_turn(mother_id, "model", response.text)
        return response.text


class ReminderAgent:
    @staticmethod
    def create_reminder(mother_id: str, title: str, category: str, scheduled_time: datetime) -> str:
        doc_ref = db.collection("reminders").document()
        doc_ref.set({
            "mother_id": mother_id,
            "title": title,
            "category": category,
            "scheduled_time": scheduled_time,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return doc_ref.id

    @staticmethod
    def check_upcoming_events(mother_id: str) -> List[Dict[str, Any]]:
        docs = db.collection("reminders")\
                 .where("mother_id", "==", mother_id)\
                 .where("status", "==", "pending")\
                 .stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]

    @staticmethod
    def generate_notification(reminder: Dict[str, Any]) -> str:
        prompt = f"""
        Generate a short, encouraging push notification for a pregnant mother.
        Reminder Title: {reminder.get('title')}
        Category: {reminder.get('category')}
        Keep it empathetic, brief, and actionable with one gentle emoji.
        """
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip()


class DailyCompanionAgent:
    @staticmethod
    def generate_daily_plan(mother_id: str) -> Dict[str, Any]:
        profile = MemoryAgent.get_profile(mother_id)
        reminders = ReminderAgent.check_upcoming_events(mother_id)
        week = profile.get("pregnancy_week", 20)
        name = profile.get("name", "Mother")

        prompt = f"""
        Generate a personalized daily plan for {name} who is in week {week} of pregnancy.
        Pending Reminders: {json.dumps([r['title'] for r in reminders])}

        Return JSON format:
        {{
            "greeting": "Good morning {name} 🌸",
            "guidance_checklist": [list of 3 actionable daily tasks],
            "baby_milestone": "A brief 1-sentence development milestone for week {week}"
        }}
        """
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)