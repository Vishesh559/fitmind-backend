from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.nutrition import NutritionLog
from app.routes.auth import get_current_user

router = APIRouter()

class NutritionRequest(BaseModel):
    meal_name: str
    calories: float
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None
    meal_type: str

@router.get("/")
def get_nutrition(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    logs = db.query(NutritionLog).filter(NutritionLog.user_id == user.id).order_by(NutritionLog.date.desc()).all()
    return [{"id": l.id, "meal_name": l.meal_name, "calories": l.calories,
             "protein": l.protein, "carbs": l.carbs, "fats": l.fats,
             "meal_type": l.meal_type, "date": l.date.strftime("%Y-%m-%d")} for l in logs]

@router.post("/")
def log_nutrition(req: NutritionRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    log = NutritionLog(user_id=user.id, meal_name=req.meal_name, calories=req.calories,
                       protein=req.protein, carbs=req.carbs, fats=req.fats, meal_type=req.meal_type)
    db.add(log)
    db.commit()
    return {"message": "Meal logged"}

@router.get("/summary")
def get_summary(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    logs = db.query(NutritionLog).filter(NutritionLog.user_id == user.id).all()
    return {
        "total_calories": sum(l.calories for l in logs),
        "total_protein": sum(l.protein or 0 for l in logs),
        "total_carbs": sum(l.carbs or 0 for l in logs),
        "total_fats": sum(l.fats or 0 for l in logs),
        "total_meals": len(logs)
    }