from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.climate import ClimateReading
from app.models.location import Location
from app.schemas.climate import ClimateResponse, ClimateSummaryResponse, CurrentWeatherResponse
from app.services.climate_service import fetch_open_meteo_forecast
from app.utils.pagination import PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/climate", tags=["Climate"])


@router.get("", response_model=PaginatedResponse[ClimateResponse])
def get_climate_readings(
    state: Optional[str] = Query(None, description="State filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    is_forecast: Optional[bool] = Query(None, description="Filter historical readings vs forecast"),
    demo: Optional[bool] = Query(None, description="Filter demo records"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Returns paginated historical and forecast climate readings."""
    query = db.query(ClimateReading)

    if state:
        query = query.filter(ClimateReading.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(ClimateReading.city.ilike(f"%{city}%"))
    if district:
        query = query.filter(ClimateReading.district.ilike(f"%{district}%"))
    if is_forecast is not None:
        query = query.filter(ClimateReading.is_forecast == is_forecast)
    if demo is not None:
        query = query.filter(ClimateReading.is_demo == demo)

    query = query.order_by(ClimateReading.observed_at.desc().nullslast(), ClimateReading.forecast_hour.asc().nullslast())
    items, total, has_more = paginate_query(query, skip=skip, limit=limit)

    return PaginatedResponse(
        items=[ClimateResponse.model_validate(it) for it in items],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/summary", response_model=ClimateSummaryResponse)
def get_climate_summary(
    state: str = Query(..., description="State name"),
    city: str = Query(..., description="City name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode"),
    db: Session = Depends(get_db),
):
    """Returns average temperature, humidity, rainfall, wind speed for a city."""
    query = db.query(ClimateReading).filter(
        ClimateReading.state.ilike(f"%{state}%"),
        ClimateReading.city.ilike(f"%{city}%"),
        ClimateReading.is_forecast.is_(False),
    )
    if demo is not None:
        query = query.filter(ClimateReading.is_demo == demo)

    avg_temp = query.with_entities(func.avg(ClimateReading.temperature_c)).scalar() or 0.0
    avg_hum = query.with_entities(func.avg(ClimateReading.humidity_percent)).scalar() or 0.0
    total_rain = query.with_entities(func.sum(ClimateReading.rainfall_mm)).scalar() or 0.0
    avg_wind = query.with_entities(func.avg(ClimateReading.wind_speed_kmh)).scalar() or 0.0
    latest = query.order_by(ClimateReading.observed_at.desc().nullslast()).first()

    return ClimateSummaryResponse(
        state=state,
        city=city,
        avg_temperature_c=round(avg_temp, 1),
        avg_humidity_percent=round(avg_hum, 1),
        total_rainfall_mm=round(total_rain, 1),
        avg_wind_speed_kmh=round(avg_wind, 1),
        latest_condition=latest.weather_condition if latest else "Sunny",
    )


@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    city: str = Query("Chennai", description="City name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    db: Session = Depends(get_db),
):
    """
    Calls Open-Meteo API for real-time live weather and 3-day forecast.
    Resolves lat/lon from database if not explicitly provided.
    """
    latitude = lat
    longitude = lon

    if latitude is None or longitude is None:
        loc = db.query(Location).filter(Location.city.ilike(f"%{city}%")).first()
        if loc and loc.latitude is not None and loc.longitude is not None:
            latitude = loc.latitude
            longitude = loc.longitude
        else:
            # Fallback coordinate for Chennai or default Indian center
            latitude = 13.0827
            longitude = 80.2707

    data = await fetch_open_meteo_forecast(latitude=latitude, longitude=longitude, city=city)
    return CurrentWeatherResponse(**data)
