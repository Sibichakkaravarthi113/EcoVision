from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


class ClimateReading(Base):
    __tablename__ = "climate_readings"

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
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    weather_condition = Column(String(100), nullable=True)
    is_forecast = Column(Boolean, default=False, index=True)
    forecast_hour = Column(Integer, nullable=True)
