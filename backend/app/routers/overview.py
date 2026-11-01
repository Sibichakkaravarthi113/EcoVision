from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.air_quality import AirQualityReading
from app.models.water_quality import WaterQualityReading
from app.models.green_coverage import GreenCoverage
from app.models.waste_management import WasteManagement
from app.models.noise_pollution import NoisePollution
from app.models.traffic import TrafficCongestion
from app.models.industrial import IndustrialActivity
from app.models.climate import ClimateReading

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("")
def get_overview(
    state: Optional[str] = Query(None, description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    district: Optional[str] = Query(None, description="District name"),
    demo: Optional[bool] = Query(None, description="Filter demo mode records"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Returns an aggregated multi-dimensional overview for a location across all 8 dimensions.
    """
    def apply_filters(query, model):
        if state:
            query = query.filter(model.state.ilike(f"%{state}%"))
        if city:
            query = query.filter(model.city.ilike(f"%{city}%"))
        if district:
            query = query.filter(model.district.ilike(f"%{district}%"))
        if demo is not None:
            query = query.filter(model.is_demo == demo)
        return query

    # 1. Air Quality
    aq_q = apply_filters(db.query(AirQualityReading), AirQualityReading)
    aq_count = aq_q.count()
    if aq_count > 0:
        pm25_avg = (
            apply_filters(db.query(func.avg(AirQualityReading.value)), AirQualityReading)
            .filter(AirQualityReading.parameter == "PM2.5")
            .scalar()
        )
        pm10_avg = (
            apply_filters(db.query(func.avg(AirQualityReading.value)), AirQualityReading)
            .filter(AirQualityReading.parameter == "PM10")
            .scalar()
        )
        station_count = aq_q.distinct(AirQualityReading.station_name).count()
        air_quality_data = {
            "data_available": True,
            "station_count": station_count,
            "avg_pm25": round(pm25_avg, 2) if pm25_avg is not None else None,
            "avg_pm10": round(pm10_avg, 2) if pm10_avg is not None else None,
            "aqi_status": "Moderate" if (pm25_avg or 0) <= 60 else "Unhealthy",
        }
    else:
        air_quality_data = {"data_available": False, "station_count": 0, "avg_pm25": None, "avg_pm10": None, "aqi_status": None}

    # 2. Water Quality
    wq_q = apply_filters(db.query(WaterQualityReading), WaterQualityReading)
    wq_count = wq_q.count()
    if wq_count > 0:
        ph_avg = (
            apply_filters(db.query(func.avg(WaterQualityReading.value)), WaterQualityReading)
            .filter(WaterQualityReading.parameter.ilike("%pH%"))
            .scalar()
        )
        do_avg = (
            apply_filters(db.query(func.avg(WaterQualityReading.value)), WaterQualityReading)
            .filter(WaterQualityReading.parameter.ilike("%oxygen%"))
            .scalar()
        )
        bod_avg = (
            apply_filters(db.query(func.avg(WaterQualityReading.value)), WaterQualityReading)
            .filter(WaterQualityReading.parameter.ilike("%bod%"))
            .scalar()
        )
        wq_stations = wq_q.distinct(WaterQualityReading.station_name).count()
        water_quality_data = {
            "data_available": True,
            "station_count": wq_stations,
            "avg_ph": round(ph_avg, 2) if ph_avg is not None else None,
            "avg_do": round(do_avg, 2) if do_avg is not None else None,
            "avg_bod": round(bod_avg, 2) if bod_avg is not None else None,
        }
    else:
        water_quality_data = {"data_available": False, "station_count": 0, "avg_ph": None, "avg_do": None, "avg_bod": None}

    # 3. Green Coverage
    gc_q = apply_filters(db.query(GreenCoverage), GreenCoverage)
    gc_count = gc_q.count()
    if gc_count > 0:
        total_forest = gc_q.with_entities(func.sum(GreenCoverage.total_forest_area_sqkm)).scalar() or 0.0
        avg_pct = gc_q.with_entities(func.avg(GreenCoverage.forest_cover_percent)).scalar() or 0.0
        green_coverage_data = {
            "data_available": True,
            "total_forest_area_sqkm": round(total_forest, 2),
            "forest_cover_percent": round(avg_pct, 2),
            "district_count": gc_count,
        }
    else:
        green_coverage_data = {"data_available": False, "total_forest_area_sqkm": None, "forest_cover_percent": None, "district_count": 0}

    # 4. Waste Management
    wm_q = apply_filters(db.query(WasteManagement), WasteManagement)
    wm_count = wm_q.count()
    if wm_count > 0:
        gen = wm_q.with_entities(func.sum(WasteManagement.generated_tonnes_day)).scalar() or 0.0
        col = wm_q.with_entities(func.sum(WasteManagement.collected_tonnes_day)).scalar() or 0.0
        proc = wm_q.with_entities(func.sum(WasteManagement.processed_tonnes_day)).scalar() or 0.0
        rec_pct = wm_q.with_entities(func.avg(WasteManagement.recycling_percent)).scalar() or 0.0
        eff = round((col / gen * 100), 2) if gen > 0 else 0.0
        waste_management_data = {
            "data_available": True,
            "total_generated_tonnes_day": round(gen, 2),
            "collection_efficiency_percent": eff,
            "recycling_percent": round(rec_pct, 2),
            "processed_tonnes_day": round(proc, 2),
        }
    else:
        waste_management_data = {"data_available": False, "total_generated_tonnes_day": None, "collection_efficiency_percent": None, "recycling_percent": None}

    # 5. Noise Pollution
    np_q = apply_filters(db.query(NoisePollution), NoisePollution)
    np_count = np_q.count()
    if np_count > 0:
        day_avg = np_q.with_entities(func.avg(NoisePollution.day_db)).scalar() or 0.0
        night_avg = np_q.with_entities(func.avg(NoisePollution.night_db)).scalar() or 0.0
        noise_pollution_data = {
            "data_available": True,
            "avg_day_db": round(day_avg, 1),
            "avg_night_db": round(night_avg, 1),
            "station_count": np_count,
        }
    else:
        noise_pollution_data = {"data_available": False, "avg_day_db": None, "avg_night_db": None, "station_count": 0}

    # 6. Traffic Congestion
    tr_q = apply_filters(db.query(TrafficCongestion), TrafficCongestion)
    tr_count = tr_q.count()
    if tr_count > 0:
        speed_avg = tr_q.with_entities(func.avg(TrafficCongestion.avg_speed_kmh)).scalar() or 0.0
        congestion_mode = (
            tr_q.with_entities(TrafficCongestion.congestion_level, func.count(TrafficCongestion.id))
            .group_by(TrafficCongestion.congestion_level)
            .order_by(func.count(TrafficCongestion.id).desc())
            .first()
        )
        traffic_data = {
            "data_available": True,
            "avg_speed_kmh": round(speed_avg, 1),
            "congestion_level": congestion_mode[0] if congestion_mode else "moderate",
            "roads_monitored": tr_count,
        }
    else:
        traffic_data = {"data_available": False, "avg_speed_kmh": None, "congestion_level": None, "roads_monitored": 0}

    # 7. Industrial Activity
    ind_q = apply_filters(db.query(IndustrialActivity), IndustrialActivity)
    ind_count = ind_q.count()
    if ind_count > 0:
        compliant = ind_q.filter(IndustrialActivity.compliance_status == "compliant").count()
        comp_pct = round((compliant / ind_count * 100), 1) if ind_count > 0 else 0.0
        industrial_data = {
            "data_available": True,
            "total_industries": ind_count,
            "compliant_percent": comp_pct,
        }
    else:
        industrial_data = {"data_available": False, "total_industries": 0, "compliant_percent": None}

    # 8. Climate
    cl_q = apply_filters(db.query(ClimateReading), ClimateReading)
    cl_count = cl_q.count()
    if cl_count > 0:
        temp_avg = cl_q.with_entities(func.avg(ClimateReading.temperature_c)).scalar()
        hum_avg = cl_q.with_entities(func.avg(ClimateReading.humidity_percent)).scalar()
        latest = cl_q.order_by(ClimateReading.observed_at.desc().nullslast()).first()
        climate_data = {
            "data_available": True,
            "temperature_c": round(temp_avg, 1) if temp_avg is not None else (latest.temperature_c if latest else None),
            "humidity_percent": round(hum_avg, 1) if hum_avg is not None else (latest.humidity_percent if latest else None),
            "weather_condition": latest.weather_condition if latest else "Clear",
        }
    else:
        climate_data = {"data_available": False, "temperature_c": None, "humidity_percent": None, "weather_condition": None}

    return {
        "location": {"state": state, "city": city, "district": district},
        "air_quality": air_quality_data,
        "water_quality": water_quality_data,
        "green_coverage": green_coverage_data,
        "waste_management": waste_management_data,
        "noise_pollution": noise_pollution_data,
        "traffic": traffic_data,
        "industrial": industrial_data,
        "climate": climate_data,
    }
