from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.workout import Workout
from app.routes.auth import get_current_user

router = APIRouter()

class WorkoutRequest(BaseModel):
    name: str
    category: str
    duration: int
    calories_burned: Optional[float] = None
    notes: Optional[str] = None

@router.get("/")
def get_workouts(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    workouts = db.query(Workout).filter(Workout.user_id == user.id).order_by(Workout.date.desc()).all()
    return [{"id": w.id, "name": w.name, "category": w.category, "duration": w.duration,
             "calories_burned": w.calories_burned, "notes": w.notes,
             "date": w.date.strftime("%Y-%m-%d %H:%M:%S")} for w in workouts]

@router.post("/")
def add_workout(req: WorkoutRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    workout = Workout(user_id=user.id, name=req.name, category=req.category,
                      duration=req.duration, calories_burned=req.calories_burned, notes=req.notes)
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return {"message": "Workout logged", "id": workout.id}

@router.delete("/{workout_id}")
def delete_workout(workout_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
    return {"message": "Workout deleted"}

@router.get("/stats")
def get_stats(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token, db)
    workouts = db.query(Workout).filter(Workout.user_id == user.id).all()
    total_calories = sum(w.calories_burned or 0 for w in workouts)
    total_duration = sum(w.duration for w in workouts)
    return {
        "total_workouts": len(workouts),
        "total_calories_burned": total_calories,
        "total_duration_minutes": total_duration,
        "this_week": len([w for w in workouts if (datetime.utcnow() - w.date).days <= 7])
    }