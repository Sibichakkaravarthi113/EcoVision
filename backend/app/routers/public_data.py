import csv
import io
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/public-data", tags=["Public Environmental Data"])

ESRI_LAYER_URL = (
    "https://livingatlas.esri.in/server1/rest/services/"
    "ForestSurvey/District_Wise_Forest_Cover_2023/MapServer/0/query"
)
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WASTE_CSV_URL = (
    "https://www.data.gov.in/files/ogd20/ogdpv2dms/s3fs-public/"
    "RS_Session_267_AU_358_B_iv.csv"
)


async def _get_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def _polygon_centroid(geometry: dict[str, Any] | None) -> tuple[float | None, float | None]:
    if not geometry or not geometry.get("rings"):
        return None, None
    points = [point for ring in geometry["rings"] for point in ring]
    if not points:
        return None, None
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


@router.get("/green-coverage")
async def get_green_coverage(
    state: str | None = Query(default=None),
    district: str | None = Query(default=None),
):
    clauses = ["1=1"]
    if state:
        safe_state = state.replace("'", "''")
        clauses.append(f"statename = '{safe_state}'")
    if district:
        safe_district = district.replace("'", "''")
        clauses.append(f"districtname = '{safe_district}'")

    try:
        payload = await _get_json(
            ESRI_LAYER_URL,
            {
                "where": " AND ".join(clauses),
                "outFields": "districtname,statename,calarea,vdf2023,mdf2023,of2023,total,percalarea",
                "returnGeometry": "true",
                "outSR": "4326",
                "resultRecordCount": 200,
                "f": "json",
            },
        )
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(status_code=502, detail=f"Esri forest layer unavailable: {error}") from error

    rows = []
    for feature in payload.get("features", []):
        attributes = feature.get("attributes", {})
        longitude, latitude = _polygon_centroid(feature.get("geometry"))
        rows.append(
            {
                **attributes,
                "latitude": latitude,
                "longitude": longitude,
                "source": "Esri India Forest Survey, District Wise Forest Cover 2023",
                "data_status": "Observed government forest-cover assessment",
                "reporting_period": "2023 assessment",
            }
        )
    return rows


@router.get("/climate")
async def get_climate(city: str = Query(...)):
    try:
        geocoding = await _get_json(
            OPEN_METEO_GEOCODING_URL,
            {"name": city, "count": 1, "language": "en", "format": "json"},
        )
        result = (geocoding.get("results") or [None])[0]
        if not result:
            raise HTTPException(status_code=404, detail=f"No coordinates found for city '{city}'.")

        forecast = await _get_json(
            OPEN_METEO_FORECAST_URL,
            {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                "forecast_days": 1,
                "timezone": "auto",
            },
        )
    except HTTPException:
        raise
    except (httpx.HTTPError, KeyError, ValueError) as error:
        raise HTTPException(status_code=502, detail=f"Open-Meteo unavailable: {error}") from error

    current = forecast.get("current", {})
    return {
        "location": {
            "city": result["name"],
            "state": result.get("admin1"),
            "country": result.get("country"),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        },
        "current": {
            "observed_at": current.get("time"),
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "units": {
                "temperature": forecast.get("current_units", {}).get("temperature_2m"),
                "humidity": forecast.get("current_units", {}).get("relative_humidity_2m"),
                "precipitation": forecast.get("current_units", {}).get("precipitation"),
                "wind_speed": forecast.get("current_units", {}).get("wind_speed_10m"),
            },
            "data_status": "Current model conditions",
        },
        "hourly": {
            "time": forecast.get("hourly", {}).get("time", []),
            "temperature": forecast.get("hourly", {}).get("temperature_2m", []),
            "humidity": forecast.get("hourly", {}).get("relative_humidity_2m", []),
            "precipitation": forecast.get("hourly", {}).get("precipitation", []),
            "wind_speed": forecast.get("hourly", {}).get("wind_speed_10m", []),
            "units": forecast.get("hourly_units", {}),
            "data_status": "Hourly forecast/model output",
        },
        "source": "Open-Meteo (forecast model)",
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/waste-management")
async def get_waste_management(state: str | None = Query(default=None)):
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(WASTE_CSV_URL)
            response.raise_for_status()
            text = response.text
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 403:
            detail = (
                "Official OGD waste data is temporarily unavailable because "
                "data.gov.in denied access to the published file (HTTP 403)."
            )
        else:
            detail = f"Official OGD waste CSV unavailable upstream (HTTP {error.response.status_code})."
        raise HTTPException(status_code=502, detail=detail) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail="Official OGD waste CSV is temporarily unavailable upstream.",
        ) from error

    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        state_name = (row.get("State/UT") or "").strip()
        if state and state_name.casefold() != state.casefold():
            continue
        rows.append(
            {
                "state": state_name,
                "generated_tpd": row.get("Solid waste generated (TPD)"),
                "collected_tpd": row.get("Collected (TPD)"),
                "treated_tpd": row.get("Treated (TPD)"),
                "reporting_period": "2020-21",
                "source": "data.gov.in / CPCB Annual Report 2020-21",
                "data_status": "Historical annual government statistics",
            }
        )
    return rows
