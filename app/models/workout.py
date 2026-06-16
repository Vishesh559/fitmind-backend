from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workouts")