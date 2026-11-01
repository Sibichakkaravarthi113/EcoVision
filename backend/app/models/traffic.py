from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


class TrafficCongestion(Base):
    __tablename__ = "traffic_congestion"

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
    road_name = Column(String(200), nullable=False)
    vehicle_count_hour = Column(Integer, nullable=True)
    avg_speed_kmh = Column(Float, nullable=True)
    congestion_level = Column(String(50), nullable=False, index=True)
    peak_hour = Column(String(20), nullable=True)
