from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS LINE!
from pydantic import BaseModel
from datetime import datetime
import shutil
import os

from agents import DocumentIntelligenceAgent, MemoryAgent, ReminderAgent, DailyCompanionAgent

app = FastAPI(
    title="Sakhi-AI Agent Service API",
    description="Autonomous Maternal Care Companion powered by Gemini Vision & FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    mother_id: str
    message: str

class ReminderCreate(BaseModel):
    mother_id: str
    title: str
    category: str
    scheduled_time: datetime

class ConfirmationRequest(BaseModel):
    mother_id: str
    extracted_data: dict


@app.post("/api/documents/process")
async def process_document(mother_id: str = Form(...), file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = DocumentIntelligenceAgent.process_document_image(temp_path)
        return {"mother_id": mother_id, "extracted_data": result}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/documents/confirm")
async def confirm_document(payload: ConfirmationRequest):
    DocumentIntelligenceAgent.save_verified_document_data(payload.mother_id, payload.extracted_data)
    return {"status": "success", "message": "Document information saved."}

@app.post("/api/chat")
async def chat_with_memory(payload: ChatRequest):
    response_text = MemoryAgent.contextual_chat(payload.mother_id, payload.message)
    return {"response": response_text}

@app.post("/api/reminders/create")
async def create_reminder(payload: ReminderCreate):
    reminder_id = ReminderAgent.create_reminder(
        payload.mother_id, payload.title, payload.category, payload.scheduled_time
    )
    return {"status": "created", "reminder_id": reminder_id}

@app.get("/api/daily-companion/{mother_id}")
async def get_daily_companion_plan(mother_id: str):
    return DailyCompanionAgent.generate_daily_plan(mother_id)