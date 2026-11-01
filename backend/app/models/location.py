from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), default="India", nullable=False)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
