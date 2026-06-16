from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, workouts, nutrition, ai
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FitMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
app.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/")
def root():
    return {"message": "FitMind API running"}