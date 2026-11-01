
import csv
from datetime import datetime
from pathlib import Path

from app.database import SessionLocal
from app.models.water_quality_reading import WaterQualityReading


BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = (
    BASE_DIR
    / "data"
    / "swq_chemical_parameter_manual_cpcb_tn_2021_2025.csv"
)

SOURCE = "CPCB / National Water Data Portal"
DATA_STATUS = "observed_historical"


# All measurement columns are mapped automatically.
# The original CSV header is retained as the parameter name.
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


def clean_text(value):
    if value is None:
        return None

    value = value.strip()

    if not value or value == "-":
        return None

    return value


def parse_float(value):
    if value is None or not value.strip():
        return None

    try:
        return float(value)
    except ValueError:
        return None


def get_unit(parameter):
    if parameter == "Potential of Hydrogen (pH)":
        return "pH"

    if "(" in parameter and ")" in parameter:
        return parameter.rsplit("(", 1)[1].split(")", 1)[0]

    return "Not specified"


def main():
    if not CSV_FILE.exists():
        print(f"CSV file not found: {CSV_FILE}")
        return

    db = SessionLocal()

    inserted = 0
    skipped = 0
    already_imported = 0

    try:
        with open(
            CSV_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            parameter_columns = [
                column
                for column in reader.fieldnames
                if column not in METADATA_COLUMNS
            ]

            for row in reader:
                source_id = int(row["SlNo"])

                # Avoid importing the same source record twice.
                existing = (
                    db.query(WaterQualityReading.id)
                    .filter(
                        WaterQualityReading.source == SOURCE,
                        WaterQualityReading.source_record_id == source_id
                    )
                    .first()
                )

                if existing:
                    already_imported += 1
                    continue

                station = clean_text(row.get("Station"))

                if not station:
                    skipped += 1
                    continue

                try:
                    sampled_at = datetime.strptime(
                        row["Data Acquisition Time"].strip(),
                        "%d-%m-%Y %H:%M"
                    )
                except (ValueError, AttributeError):
                    sampled_at = None

                record_inserted = False

                for parameter in parameter_columns:
                    value = parse_float(row.get(parameter))

                    # Missing values are not converted to zero.
                    if value is None:
                        continue

                    reading = WaterQualityReading(
                        source_record_id=source_id,
                        station=station,
                        agency=clean_text(row.get("Agency")),
                        state=clean_text(row.get("State")),
                        district=clean_text(row.get("District")),
                        tehsil=clean_text(row.get("Tehsil")),
                        block=clean_text(row.get("Block")),
                        village=clean_text(row.get("Village")),
                        river=clean_text(row.get("River")),
                        basin=clean_text(row.get("Basin")),
                        tributary=clean_text(row.get("Tributary")),
                        local_river=clean_text(row.get("Local River")),
                        latitude=parse_float(row.get("Latitude")),
                        longitude=parse_float(row.get("Longitude")),
                        parameter=parameter,
                        value=value,
                        unit=get_unit(parameter),
                        sampled_at=sampled_at,
                        source=SOURCE,
                        data_status=DATA_STATUS,
                    )

                    db.add(reading)
                    inserted += 1
                    record_inserted = True

                if not record_inserted:
                    skipped += 1

                # Save in batches.
                if inserted > 0 and inserted % 200 == 0:
                    db.commit()

        db.commit()

        print("\nWATER QUALITY IMPORT COMPLETED")
        print("--------------------------------")
        print(f"Measurements inserted: {inserted}")
        print(f"Source rows skipped: {skipped}")
        print(f"Already imported rows: {already_imported}")
        print("--------------------------------")

    except Exception as error:
        db.rollback()
        print("Import failed:", error)

    finally:
        db.close()


if __name__ == "__main__":
    main()
