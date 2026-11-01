import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal
from app.models.air_quality import AirQualityReading
from app.models.location import Location
from scripts.generate_demo_data import get_aqi_category

JSON_FILE = BASE_DIR / "data" / "cpcb_air_quality.json"
DATA_SOURCE = "CPCB / data.gov.in"
DATA_STATUS = "real"

POLLUTANT_UNITS = {
    "PM2.5": "µg/m³",
    "PM10": "µg/m³",
    "NO2": "µg/m³",
    "SO2": "µg/m³",
    "OZONE": "µg/m³",
    "NH3": "µg/m³",
    "CO": "mg/m³",
}


def parse_float(val):
    if val in (None, "", "NA", "N/A", "-", "null"):
        return None
    try:
        f = float(val)
        if f != f or f in (float("inf"), float("-inf")):
            return None
        return f
    except (ValueError, TypeError):
        return None


def parse_dt(val):
    if not val:
        return None
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(val.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def main():
    if not JSON_FILE.exists():
        print(f"Error: JSON file not found at {JSON_FILE}")
        return

    print(f"Loading CPCB air quality readings from {JSON_FILE}...")
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    print(f"Total records in JSON: {len(records)}")

    db = SessionLocal()

    inserted = 0
    duplicates_skipped = 0
    invalid_skipped = 0

    try:
        # Load existing (station, parameter, observed_at) keys to prevent duplicates
        print("Indexing existing air quality records to avoid duplicates...")
        existing_rows = (
            db.query(
                AirQualityReading.station_name,
                AirQualityReading.parameter,
                AirQualityReading.observed_at,
            )
            .filter(AirQualityReading.data_source == DATA_SOURCE)
            .all()
        )
        existing_keys = {
            (r[0], r[1], r[2]) for r in existing_rows
        }
        print(f"Found {len(existing_keys)} existing keys in DB.")

        # Also keep track of locations to add any new cities
        existing_locations = {
            (r.state.lower(), r.city.lower())
            for r in db.query(Location.state, Location.city).filter(Location.city.isnot(None)).all()
        }
        new_locations = []

        batch = []
        for rec in records:
            state = (rec.get("state") or "").strip()
            city = (rec.get("city") or "").strip()
            station = (rec.get("station") or "").strip()
            param = (rec.get("pollutant_id") or "").strip().upper()
            val = parse_float(rec.get("avg_value"))
            observed_at = parse_dt(rec.get("last_update"))

            if not state or not city or not station or not param or val is None or observed_at is None:
                invalid_skipped += 1
                continue

            dedup_key = (station, param, observed_at)
            if dedup_key in existing_keys:
                duplicates_skipped += 1
                continue

            existing_keys.add(dedup_key)

            lat = parse_float(rec.get("latitude"))
            lon = parse_float(rec.get("longitude"))
            unit = POLLUTANT_UNITS.get(param, "µg/m³")
            cat = get_aqi_category(param, val)

            reading = AirQualityReading(
                state=state,
                district=city,
                city=city,
                station_name=station,
                latitude=lat,
                longitude=lon,
                data_source=DATA_SOURCE,
                observed_at=observed_at,
                data_status=DATA_STATUS,
                is_demo=False,
                parameter=param,
                value=val,
                unit=unit,
                pollutant_category=cat,
            )
            batch.append(reading)

            # Record location if new
            loc_key = (state.lower(), city.lower())
            if loc_key not in existing_locations:
                existing_locations.add(loc_key)
                new_locations.append(Location(
                    country="India",
                    state=state,
                    district=city,
                    city=city,
                    latitude=lat,
                    longitude=lon,
                ))

            if len(batch) >= 250:
                db.bulk_save_objects(batch)
                db.commit()
                inserted += len(batch)
                batch = []

        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            inserted += len(batch)

        if new_locations:
            db.bulk_save_objects(new_locations)
            db.commit()
            print(f"Added {len(new_locations)} new locations from CPCB dataset.")

        print("\n==========================================")
        print("CPCB AIR QUALITY IMPORT SUMMARY")
        print("==========================================")
        print(f"Total source records in file : {len(records)}")
        print(f"Successfully imported        : {inserted}")
        print(f"Duplicates skipped           : {duplicates_skipped}")
        print(f"Invalid / missing skipped    : {invalid_skipped}")
        print("==========================================")

    except Exception as exc:
        db.rollback()
        print(f"CPCB Air Quality Import Failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
