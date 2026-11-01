
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base


class EnvironmentalReading(Base):
    __tablename__ = "environmental_readings"

    id = Column(Integer, primary_key=True, index=True)

    # Environmental module
    factor = Column(String(50), nullable=False, index=True)

    # Measurement details
    parameter = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False)

    # Geographic information
    location_name = Column(String(150), nullable=False)
    state = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    station = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Data transparency
    source = Column(String(200), nullable=False)
    data_status = Column(String(30), nullable=False)

    # Measurement timestamps
    observed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
