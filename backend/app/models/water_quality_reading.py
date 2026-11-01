
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index
)

from app.database import Base


class WaterQualityReading(Base):
    __tablename__ = "water_quality_readings"

    id = Column(Integer, primary_key=True, index=True)

    # Original CSV record
    source_record_id = Column(Integer, nullable=True)

    # Location information
    station = Column(String(300), nullable=False, index=True)
    agency = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True, index=True)
    tehsil = Column(String(100), nullable=True)
    block = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)

    # Water body information
    river = Column(String(200), nullable=True)
    basin = Column(String(200), nullable=True)
    tributary = Column(String(200), nullable=True)
    local_river = Column(String(200), nullable=True)

    # Geographic coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Water quality measurement
    parameter = Column(String(150), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)

    # Sampling information
    sampled_at = Column(DateTime, nullable=True, index=True)

    # Data source and status
    source = Column(String(200), nullable=False)
    data_status = Column(String(50), nullable=False)

    __table_args__ = (
        Index(
            "ix_water_location_parameter",
            "state",
            "district",
            "parameter"
        ),
    )
