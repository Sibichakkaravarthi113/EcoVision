from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.database import Base


class DemoEnvironmentalRecord(Base):
    __tablename__ = "demo_environmental_records"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(50), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    observed_at = Column(DateTime, nullable=True, index=True)
    source = Column(String(200), nullable=False)
    data_status = Column(String(30), nullable=False, default="synthetic_demo")
    is_real_measurement = Column(Boolean, nullable=False, default=False)
    payload = Column(Text, nullable=False)


class DemoLocation(Base):
    __tablename__ = "demo_locations"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
