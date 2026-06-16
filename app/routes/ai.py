from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import requests as req
import os
from app.database import get_db
from app.models.workout import Workout
from app.models.nutrition import NutritionLog
from app.routes.auth import get_current_user

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@router.post("/chat")
def ai_chat(req_body: ChatRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)

    workouts = db.query(Workout).filter(Workout.user_id == user.id).limit(10).all()

    context = f"User: {user.name}, Goal: {user.goal}, Weight: {user.weight}kg, Height: {user.height}cm. Recent workouts: {[w.name + ' ' + str(w.duration) + 'min' for w in workouts]}"

    system = f"You are FitMind AI, an expert personal fitness coach. User data: {context}. Give specific actionable advice. Be encouraging and concise. Under 150 words."

    response = req.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY', '')}",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 500,
            "messages": [{"role": "system", "content": system}] + [{"role": m.role, "content": m.content} for m in req_body.messages],
        }
    )
    result = response.json()
    if "choices" in result:
        return {"reply": result["choices"][0]["message"]["content"]}
    return {"reply": "Sorry I had trouble connecting. Please try again."}

@router.post("/generate-workout")
def generate_workout(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)

    response = req.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY', '')}",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": f"Create a workout plan for goal: {user.goal}, weight: {user.weight}kg. Include 5 exercises with sets and reps. Be concise."}],
        }
    )
    result = response.json()
    if "choices" in result:
        return {"plan": result["choices"][0]["message"]["content"]}
    return {"plan": "Could not generate plan."}