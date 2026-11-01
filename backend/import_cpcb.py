
import json
from pathlib import Path
from datetime import datetime

from app.database import SessionLocal
from app.models.environmental_reading import EnvironmentalReading


# File location
BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = BASE_DIR / "data" / "cpcb_air_quality.json"

# CPCB pollutant units
POLLUTANT_UNITS = {
    "PM2.5": "µg/m³",
    "PM10": "µg/m³",
    "NO2": "µg/m³",
    "SO2": "µg/m³",
    "OZONE": "µg/m³",
    "NH3": "µg/m³",
    "CO": "mg/m³",
}

SOURCE_NAME = "CPCB / data.gov.in"
DATA_STATUS = "observed_snapshot"


def parse_number(value):
    if value in (None, "", "NA", "N/A"):
        return None

    try:
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            return None
        return number
    except (ValueError, TypeError):
        return None


def parse_timestamp(value):
    try:
        return datetime.strptime(value, "%d-%m-%Y %H:%M:%S")
    except (ValueError, TypeError):
        return None


def main():
    if not JSON_FILE.exists():
        print("ERROR: CPCB JSON file not found:", JSON_FILE)
        return

    with JSON_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = data.get("records", [])

    db = SessionLocal()

    inserted = 0
    missing_values = 0
    invalid_records = 0
    duplicates = 0

    try:
        # Load existing CPCB records to prevent duplicate imports
        existing_rows = (
            db.query(
                EnvironmentalReading.state,
                EnvironmentalReading.city,
                EnvironmentalReading.station,
                EnvironmentalReading.parameter,
                EnvironmentalReading.observed_at
            )
            .filter(EnvironmentalReading.source == SOURCE_NAME)
            .all()
        )

        existing_keys = {
            (
                row.state,
                row.city,
                row.station,
                row.parameter,
                row.observed_at
            )
            for row in existing_rows
        }

        for record in records:
            pollutant = record.get("pollutant_id", "").strip().upper()

            if pollutant not in POLLUTANT_UNITS:
                invalid_records += 1
                continue

            value = parse_number(record.get("avg_value"))

            if value is None:
                missing_values += 1
                continue

            state = record.get("state", "").strip()
            city = record.get("city", "").strip()
            station = record.get("station", "").strip()

            observed_at = parse_timestamp(record.get("last_update"))

            if not state or not city or not station or observed_at is None:
                invalid_records += 1
                continue

            key = (
                state,
                city,
                station,
                pollutant,
                observed_at
            )

            if key in existing_keys:
                duplicates += 1
                continue

            latitude = parse_number(record.get("latitude"))
            longitude = parse_number(record.get("longitude"))

            reading = EnvironmentalReading(
                factor="Air Quality",
                parameter=pollutant,
                value=value,
                unit=POLLUTANT_UNITS[pollutant],
                location_name=station,
                state=state,
                city=city,
                station=station,
                latitude=latitude,
                longitude=longitude,
                source=SOURCE_NAME,
                data_status=DATA_STATUS,
                observed_at=observed_at
            )

            db.add(reading)
            existing_keys.add(key)
            inserted += 1

            # Commit in batches
            if inserted % 250 == 0:
                db.commit()
                print(f"Imported {inserted} records...")

        db.commit()

        print("\n========== CPCB IMPORT SUMMARY ==========")
        print("Total source records:", len(records))
        print("Successfully imported:", inserted)
        print("Missing average values:", missing_values)
        print("Duplicate records skipped:", duplicates)
        print("Invalid records skipped:", invalid_records)
        print("=========================================")

    except Exception as error:
        db.rollback()
        print("IMPORT FAILED:", error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
