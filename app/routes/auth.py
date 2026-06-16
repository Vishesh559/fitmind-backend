from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from app.database import get_db
from app.models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
ALGORITHM = "HS256"

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int = None
    weight: float = None
    height: float = None
    goal: str = None

class LoginRequest(BaseModel):
    email: str
    password: str

def create_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return db.query(User).filter(User.id == user_id).first()
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=req.name,
        email=req.email,
        password=pwd_context.hash(req.password),
        age=req.age,
        weight=req.weight,
        height=req.height,
        goal=req.goal,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Account created", "token": create_token(user.id), "user": {"id": user.id, "name": user.name, "email": user.email}}

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not pwd_context.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(user.id), "user": {"id": user.id, "name": user.name, "email": user.email, "goal": user.goal}}