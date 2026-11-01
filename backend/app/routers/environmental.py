
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from app.database import get_db
from app.models.environmental_reading import EnvironmentalReading
from app.schemas.environmental import (
    EnvironmentalReadingCreate,
    EnvironmentalReadingResponse
)

router = APIRouter(
    prefix="/api/environmental",
    tags=["Environmental Data"]
)


# 1. Create a new environmental reading
@router.post(
    "/readings",
    response_model=EnvironmentalReadingResponse
)
def create_reading(
    reading: EnvironmentalReadingCreate,
    db: Session = Depends(get_db)
):
    new_reading = EnvironmentalReading(**reading.model_dump())

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading


# 2. Get all readings
@router.get(
    "/readings",
    response_model=list[EnvironmentalReadingResponse]
)
def get_readings(db: Session = Depends(get_db)):
    return db.query(EnvironmentalReading).all()


# 3. Filter readings by state, city and pollutant
# IMPORTANT: Keep this route before /readings/{factor}
@router.get(
    "/readings/location",
    response_model=list[EnvironmentalReadingResponse]
)
def get_location_readings(
    state: str = Query(...),
    city: str = Query(None),
    pollutant: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(EnvironmentalReading).filter(
        EnvironmentalReading.source == "CPCB / data.gov.in",
        EnvironmentalReading.state.ilike(state)
    )

    if city:
        query = query.filter(
            EnvironmentalReading.city.ilike(city)
        )

    if pollutant:
        query = query.filter(
            EnvironmentalReading.parameter.ilike(pollutant)
        )

    return query.order_by(
        EnvironmentalReading.city,
        EnvironmentalReading.station,
        EnvironmentalReading.parameter
    ).all()


# 4. Get readings by environmental factor
@router.get(
    "/readings/{factor}",
    response_model=list[EnvironmentalReadingResponse]
)
def get_readings_by_factor(
    factor: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(EnvironmentalReading)
        .filter(EnvironmentalReading.factor.ilike(factor))
        .all()
    )


# 5. Get readings by location name
@router.get(
    "/location/{location_name}",
    response_model=list[EnvironmentalReadingResponse]
)
def get_readings_by_location(
    location_name: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(EnvironmentalReading)
        .filter(
            EnvironmentalReading.location_name.ilike(location_name)
        )
        .all()
    )


# 6. Get all available states
@router.get("/states")
def get_states(db: Session = Depends(get_db)):
    states = (
        db.query(distinct(EnvironmentalReading.state))
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in",
            EnvironmentalReading.state.isnot(None)
        )
        .order_by(EnvironmentalReading.state)
        .all()
    )

    return [state[0] for state in states]


# 7. Get cities in a selected state
@router.get("/cities/{state}")
def get_cities(
    state: str,
    db: Session = Depends(get_db)
):
    cities = (
        db.query(distinct(EnvironmentalReading.city))
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in",
            EnvironmentalReading.state.ilike(state),
            EnvironmentalReading.city.isnot(None)
        )
        .order_by(EnvironmentalReading.city)
        .all()
    )

    return [city[0] for city in cities]


# 8. Get monitoring stations
@router.get("/stations")
def get_stations(
    state: str = Query(None),
    city: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(EnvironmentalReading).filter(
        EnvironmentalReading.source == "CPCB / data.gov.in"
    )

    if state:
        query = query.filter(
            EnvironmentalReading.state.ilike(state)
        )

    if city:
        query = query.filter(
            EnvironmentalReading.city.ilike(city)
        )

    stations = (
        query.with_entities(distinct(EnvironmentalReading.station))
        .filter(EnvironmentalReading.station.isnot(None))
        .order_by(EnvironmentalReading.station)
        .all()
    )

    return [station[0] for station in stations]


# 9. Get available pollutants
@router.get("/pollutants")
def get_pollutants(db: Session = Depends(get_db)):
    pollutants = (
        db.query(distinct(EnvironmentalReading.parameter))
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in",
            EnvironmentalReading.parameter.isnot(None)
        )
        .order_by(EnvironmentalReading.parameter)
        .all()
    )

    return [pollutant[0] for pollutant in pollutants]
