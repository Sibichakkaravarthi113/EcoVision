import sys
import csv
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal
from app.models.water_quality import WaterQualityReading
from app.models.location import Location

CSV_FILE = BASE_DIR / "data" / "swq_chemical_parameter_manual_cpcb_tn_2021_2025.csv"
DATA_SOURCE = "CPCB / National Water Data Portal"
DATA_STATUS = "real"

METADATA_COLUMNS = {
    "SlNo",
    "Station",
    "Agency",
    "State LGD Code",
    "State",
    "District LGD Code",
    "District",
    "Tehsil",
    "Block",
    "Village",
    "River",
    "Basin",
    "Tributary",
    "Subtributary",
    "SubSubtributary",
    "Local River",
    "Latitude",
    "Longitude",
    "Data Acquisition Time",
}


def clean_text(val):
    if not val:
        return None
    val = val.strip()
    if not val or val == "-":
        return None
    return val


def parse_float(val):
    if not val:
        return None
    val = str(val).strip()
    if val in ("", "NA", "N/A", "-", "null"):
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
    val = val.strip()
    for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val, fmt)
        except (ValueError, AttributeError):
            continue
    return None


def get_unit(param: str) -> str:
    if "pH" in param:
        return "pH"
    if "(" in param and ")" in param:
        return param.rsplit("(", 1)[1].split(")", 1)[0].strip()
    return "mg/L"


def main():
    if not CSV_FILE.exists():
        print(f"Error: CSV file not found at {CSV_FILE}")
        return

    print(f"Loading CPCB water quality readings from {CSV_FILE}...")
    db = SessionLocal()

    inserted = 0
    duplicates_skipped = 0
    source_rows_processed = 0

    try:
        # Load existing keys
        print("Indexing existing water quality records to avoid duplicates...")
        existing_rows = (
            db.query(
                WaterQualityReading.station_name,
                WaterQualityReading.parameter,
                WaterQualityReading.observed_at,
            )
            .filter(WaterQualityReading.data_source == DATA_SOURCE)
            .all()
        )
        existing_keys = {(r[0], r[1], r[2]) for r in existing_rows}
        print(f"Found {len(existing_keys)} existing keys in DB.")

        existing_locations = {
            (r.state.lower(), (r.city or "").lower())
            for r in db.query(Location.state, Location.city).filter(Location.city.isnot(None)).all()
        }
        new_locations = []

        batch = []
        with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            param_cols = [c for c in reader.fieldnames if c not in METADATA_COLUMNS]

            for row in reader:
                source_rows_processed += 1
                station = clean_text(row.get("Station"))
                state = clean_text(row.get("State")) or "Tamil Nadu"
                district = clean_text(row.get("District"))
                tehsil = clean_text(row.get("Tehsil"))
                city = district or tehsil or "Tamil Nadu"
                sl_no = row.get("SlNo", "").strip()

                if not station:
                    continue

                lat = parse_float(row.get("Latitude"))
                lon = parse_float(row.get("Longitude"))
                observed_at = parse_dt(row.get("Data Acquisition Time"))
                station_code = f"TN-CPCB-{sl_no}" if sl_no else None

                # Location update
                if city:
                    loc_key = (state.lower(), city.lower())
                    if loc_key not in existing_locations:
                        existing_locations.add(loc_key)
                        new_locations.append(Location(
                            country="India",
                            state=state,
                            district=district,
                            city=city,
                            latitude=lat,
                            longitude=lon,
                        ))

                for param in param_cols:
                    val = parse_float(row.get(param))
                    if val is None:
                        continue

                    dedup_key = (station, param, observed_at)
                    if dedup_key in existing_keys:
                        duplicates_skipped += 1
                        continue

                    existing_keys.add(dedup_key)
                    unit = get_unit(param)

                    reading = WaterQualityReading(
                        state=state,
                        district=district,
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
                        station_code=station_code,
                    )
                    batch.append(reading)

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
            print(f"Added {len(new_locations)} new locations from water dataset.")

        print("\n==========================================")
        print("CPCB WATER QUALITY IMPORT SUMMARY")
        print("==========================================")
        print(f"Total source rows processed  : {source_rows_processed}")
        print(f"Total measurements inserted  : {inserted}")
        print(f"Duplicates skipped           : {duplicates_skipped}")
        print("==========================================")

    except Exception as exc:
        db.rollback()
        print(f"Water Quality Import Failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
