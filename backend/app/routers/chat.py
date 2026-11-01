import re
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
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
from app.models.location import Location

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class LocationContext(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    location: Optional[LocationContext] = None
    demo_mode: bool = False
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    reply: str
    sources: List[str]
    data_used: List[Dict[str, Any]]


def detect_city(text: str, db: Session) -> Optional[tuple[str, str]]:
    """Tries to extract a known city and state from the user's message."""
    words = re.findall(r"\b[A-Za-z]+\b", text)
    for word in words:
        loc = db.query(Location).filter(Location.city.ilike(word)).first()
        if loc and loc.city:
            return loc.city, loc.state
    return None


@router.post("", response_model=ChatResponse)
def handle_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Deterministic, rule-based environmental assistant that directly queries the database
    and returns factual responses with data citations.
    """
    msg = payload.message.lower().strip()
    demo_mode = payload.demo_mode

    # Resolve location
    detected = detect_city(payload.message, db)
    if detected:
        city, state = detected
    elif payload.location:
        city = payload.location.city or "Chennai"
        state = payload.location.state or "Tamil Nadu"
    else:
        city, state = "Chennai", "Tamil Nadu"

    sources: List[str] = []
    data_used: List[Dict[str, Any]] = []
    reply_lines: List[str] = []

    # Intent detection
    is_air = any(w in msg for w in ["air", "pm2.5", "pm10", "aqi", "smog", "ozone", "no2", "so2", "nh3", "breath"])
    is_water = any(w in msg for w in ["water", "ph", "oxygen", "do", "bod", "tds", "river", "lake", "potable", "coliform"])
    is_green = any(w in msg for w in ["green", "forest", "tree", "canopy", "vegetation", "coverage", "fsi"])
    is_waste = any(w in msg for w in ["waste", "garbage", "trash", "recycle", "landfill", "tpd", "collection"])
    is_noise = any(w in msg for w in ["noise", "decibel", "sound", "acoustic", "db", "silence", "loud"])
    is_traffic = any(w in msg for w in ["traffic", "congestion", "road", "vehicle", "speed", "jam", "rush hour"])
    is_industry = any(w in msg for w in ["industry", "industrial", "factory", "compliance", "emissions", "consent"])
    is_climate = any(w in msg for w in ["climate", "weather", "temperature", "temp", "rain", "rainfall", "humidity", "wind", "forecast"])

    # If no specific dimension was detected, provide a multi-dimensional summary
    if not any([is_air, is_water, is_green, is_waste, is_noise, is_traffic, is_industry, is_climate]):
        if any(w in msg for w in ["hello", "hi", "hey", "help", "who are you"]):
            return ChatResponse(
                reply=(
                    f"Hello! I am EcoVision's Environmental Data Assistant. "
                    f"I provide real-time and historical analytics across 8 environmental dimensions for {city}, {state}. "
                    f"You can ask me about Air Quality (PM2.5, NO2), Water Quality (pH, DO), Green Coverage, "
                    f"Waste Management, Noise Pollution, Traffic Congestion, Industrial Compliance, or Climate Conditions."
                ),
                sources=["EcoVision Knowledge Base"],
                data_used=[],
            )
        # Default overview
        is_air = is_water = is_climate = True

    # 1. Process Air Quality query
    if is_air:
        aq_q = db.query(AirQualityReading).filter(
            AirQualityReading.city.ilike(f"%{city}%"),
            AirQualityReading.is_demo == demo_mode,
        )
        readings = aq_q.all()
        if readings:
            pm25 = next((r for r in readings if r.parameter.upper() == "PM2.5"), None)
            pm10 = next((r for r in readings if r.parameter.upper() == "PM10"), None)
            no2 = next((r for r in readings if r.parameter.upper() == "NO2"), None)
            
            air_summary = []
            if pm25:
                air_summary.append(f"PM2.5: {pm25.value} {pm25.unit} ({pm25.pollutant_category})")
                data_used.append({"dimension": "air_quality", "parameter": "PM2.5", "value": pm25.value, "unit": pm25.unit})
            if pm10:
                air_summary.append(f"PM10: {pm10.value} {pm10.unit}")
                data_used.append({"dimension": "air_quality", "parameter": "PM10", "value": pm10.value, "unit": pm10.unit})
            if no2:
                air_summary.append(f"NO2: {no2.value} {no2.unit}")
                data_used.append({"dimension": "air_quality", "parameter": "NO2", "value": no2.value, "unit": no2.unit})

            source_name = readings[0].data_source
            if source_name not in sources:
                sources.append(source_name)

            reply_lines.append(
                f"🌫️ **Air Quality in {city}**:\n"
                f"Current recorded levels: {', '.join(air_summary)}.\n"
                f"CPCB National Ambient Air Quality standard for PM2.5 24-hour average is 60 µg/m³."
            )
        else:
            reply_lines.append(f"🌫️ No specific air quality records found in the database for {city} (mode: {'demo' if demo_mode else 'public'}).")

    # 2. Process Water Quality query
    if is_water:
        wq_q = db.query(WaterQualityReading).filter(
            (WaterQualityReading.city.ilike(f"%{city}%")) | (WaterQualityReading.state.ilike(f"%{state}%")),
            WaterQualityReading.is_demo == demo_mode,
        )
        readings = wq_q.limit(10).all()
        if readings:
            ph = next((r for r in readings if "ph" in r.parameter.lower()), None)
            do = next((r for r in readings if "oxygen" in r.parameter.lower() or "do" in r.parameter.lower()), None)
            
            wq_summary = []
            if ph:
                wq_summary.append(f"pH {ph.value} {ph.unit}")
                data_used.append({"dimension": "water_quality", "parameter": "pH", "value": ph.value, "unit": ph.unit})
            if do:
                wq_summary.append(f"Dissolved Oxygen {do.value} {do.unit}")
                data_used.append({"dimension": "water_quality", "parameter": "DO", "value": do.value, "unit": do.unit})

            source_name = readings[0].data_source
            if source_name not in sources:
                sources.append(source_name)

            status = "potable and healthy" if (ph and 6.5 <= ph.value <= 8.5) else "requires treatment"
            reply_lines.append(
                f"💧 **Water Quality for {city} ({state})**:\n"
                f"Measurements indicate {', '.join(wq_summary) if wq_summary else 'records available across monitoring stations'}. "
                f"Water conditions are categorized as {status} relative to CPCB Class C inland water standards."
            )
        else:
            reply_lines.append(f"💧 No water quality readings available for {city} in {'demo' if demo_mode else 'public'} mode.")

    # 3. Process Green Coverage query
    if is_green:
        gc = db.query(GreenCoverage).filter(
            GreenCoverage.state.ilike(f"%{state}%"),
            GreenCoverage.is_demo == demo_mode,
        ).first()
        if gc:
            data_used.append({"dimension": "green_coverage", "forest_cover_percent": gc.forest_cover_percent, "forest_area_sqkm": gc.total_forest_area_sqkm})
            if gc.data_source not in sources:
                sources.append(gc.data_source)
            reply_lines.append(
                f"🌳 **Green Coverage in {state}**:\n"
                f"Total forest cover stands at {gc.total_forest_area_sqkm:,.1f} sq km, representing "
                f"{gc.forest_cover_percent:.1f}% of geographic area (Very dense: {gc.very_dense_forest:.1f} sq km). "
                f"National Forest Policy targets a minimum of 33% forest cover."
            )
        else:
            reply_lines.append(f"🌳 Green coverage statistics not recorded for {state}.")

    # 4. Process Waste Management query
    if is_waste:
        wm = db.query(WasteManagement).filter(
            WasteManagement.city.ilike(f"%{city}%"),
            WasteManagement.is_demo == demo_mode,
        ).first()
        if wm:
            data_used.append({"dimension": "waste_management", "generated_tonnes_day": wm.generated_tonnes_day, "recycling_percent": wm.recycling_percent})
            if wm.data_source not in sources:
                sources.append(wm.data_source)
            collection_eff = round(wm.collected_tonnes_day / wm.generated_tonnes_day * 100, 1) if wm.generated_tonnes_day > 0 else 0
            reply_lines.append(
                f"♻️ **Waste Management in {city}**:\n"
                f"Daily solid waste generation is {wm.generated_tonnes_day:,.0f} tonnes/day with a collection efficiency of "
                f"{collection_eff}%. Recycled share is {wm.recycling_percent:.1f}% with {wm.processed_tonnes_day:,.0f} tonnes processed daily."
            )
        else:
            reply_lines.append(f"♻️ Waste management figures for {city} are not catalogued.")

    # 5. Process Noise Pollution query
    if is_noise:
        np_rows = db.query(NoisePollution).filter(
            NoisePollution.city.ilike(f"%{city}%"),
            NoisePollution.is_demo == demo_mode,
        ).all()
        if np_rows:
            day_avg = sum(r.day_db for r in np_rows) / len(np_rows)
            night_avg = sum(r.night_db for r in np_rows) / len(np_rows)
            data_used.append({"dimension": "noise_pollution", "avg_day_db": round(day_avg, 1), "avg_night_db": round(night_avg, 1)})
            if np_rows[0].data_source not in sources:
                sources.append(np_rows[0].data_source)
            reply_lines.append(
                f"🔊 **Acoustic Environment in {city}**:\n"
                f"Average ambient sound levels are {day_avg:.1f} dB(A) daytime and {night_avg:.1f} dB(A) nighttime across {len(np_rows)} monitoring points. "
                f"CPCB daytime limit for residential zones is 55 dB(A)."
            )
        else:
            reply_lines.append(f"🔊 Noise pollution data not found for {city}.")

    # 6. Process Traffic Congestion query
    if is_traffic:
        tr_rows = db.query(TrafficCongestion).filter(
            TrafficCongestion.city.ilike(f"%{city}%"),
            TrafficCongestion.is_demo == demo_mode,
        ).all()
        if tr_rows:
            avg_spd = sum(r.avg_speed_kmh for r in tr_rows if r.avg_speed_kmh) / max(len(tr_rows), 1)
            busiest = max(tr_rows, key=lambda r: r.vehicle_count_hour or 0)
            data_used.append({"dimension": "traffic", "avg_speed_kmh": round(avg_spd, 1), "busiest_corridor": busiest.road_name})
            if tr_rows[0].data_source not in sources:
                sources.append(tr_rows[0].data_source)
            reply_lines.append(
                f"🚗 **Traffic Conditions in {city}**:\n"
                f"Monitored corridors report an average vehicular speed of {avg_spd:.1f} km/h. "
                f"Heaviest corridor: {busiest.road_name} with ~{busiest.vehicle_count_hour} vehicles/hour ({busiest.congestion_level} congestion)."
            )
        else:
            reply_lines.append(f"🚗 No vehicular traffic data recorded for {city}.")

    # 7. Process Industrial query
    if is_industry:
        ind_rows = db.query(IndustrialActivity).filter(
            IndustrialActivity.city.ilike(f"%{city}%"),
            IndustrialActivity.is_demo == demo_mode,
        ).all()
        if ind_rows:
            comp_count = sum(1 for r in ind_rows if r.compliance_status == "compliant")
            comp_pct = round(comp_count / len(ind_rows) * 100, 1)
            data_used.append({"dimension": "industrial", "total_units": len(ind_rows), "compliance_rate": comp_pct})
            if ind_rows[0].data_source not in sources:
                sources.append(ind_rows[0].data_source)
            reply_lines.append(
                f"🏭 **Industrial Compliance in {city}**:\n"
                f"{len(ind_rows)} industrial facilities monitored; regulatory compliance rate is {comp_pct}% "
                f"under State Pollution Control Board guidelines."
            )
        else:
            reply_lines.append(f"🏭 Industrial registry records not found for {city}.")

    # 8. Process Climate query
    if is_climate:
        cl_row = db.query(ClimateReading).filter(
            ClimateReading.city.ilike(f"%{city}%"),
            ClimateReading.is_demo == demo_mode,
            ClimateReading.is_forecast.is_(False),
        ).order_by(ClimateReading.observed_at.desc().nullslast()).first()
        if cl_row:
            data_used.append({
                "dimension": "climate",
                "temperature_c": cl_row.temperature_c,
                "humidity_percent": cl_row.humidity_percent,
                "rainfall_mm": cl_row.rainfall_mm,
            })
            if cl_row.data_source not in sources:
                sources.append(cl_row.data_source)
            reply_lines.append(
                f"☀️ **Climate Profile for {city}**:\n"
                f"Observed temperature: {cl_row.temperature_c}°C, Relative humidity: {cl_row.humidity_percent}%, "
                f"Wind speed: {cl_row.wind_speed_kmh} km/h, Weather condition: {cl_row.weather_condition}."
            )
        else:
            reply_lines.append(f"☀️ Climate readings not found for {city}.")

    final_reply = "\n\n".join(reply_lines)
    return ChatResponse(
        reply=final_reply,
        sources=sources if sources else ["CPCB / data.gov.in", "EcoVision Knowledge Engine"],
        data_used=data_used,
    )
