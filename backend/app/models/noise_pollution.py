from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


class NoisePollution(Base):
    __tablename__ = "noise_pollution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=False, index=True)
    station_name = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    data_source = Column(String(200), nullable=False)
    observed_at = Column(DateTime, nullable=True)
    data_status = Column(String(50), default="real")
    is_demo = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Extra fields
    location_type = Column(String(50), nullable=False, index=True)
    day_db = Column(Float, nullable=False)
    night_db = Column(Float, nullable=False)
    measurement_period = Column(String(50), nullable=False)
