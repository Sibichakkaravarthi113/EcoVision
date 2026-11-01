import argparse
import csv
import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models.demo_environmental_record import DemoEnvironmentalRecord, DemoLocation


FILES = {
    "air_quality_demo.csv": "air_quality",
    "water_quality_demo.csv": "water_quality",
    "green_coverage_demo.csv": "green_coverage",
    "waste_management_demo.csv": "waste_management",
    "noise_pollution_demo.csv": "noise_pollution",
    "traffic_congestion_demo.csv": "traffic_congestion",
    "industrial_activity_demo.csv": "industrial_activity",
    "climate_conditions_demo.csv": "climate_conditions",
}


def parse_datetime(value):
    if not value:
        return None
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    raise ValueError(f"Unsupported timestamp: {value}")


def number(value):
    return float(value) if value not in ("", None) else None


def import_bundle(zip_path: Path):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        session.query(DemoEnvironmentalRecord).delete()
        session.query(DemoLocation).delete()
        with zipfile.ZipFile(zip_path) as bundle:
            locations = csv.DictReader(io.StringIO(bundle.read("locations.csv").decode("utf-8-sig")))
            session.add_all(
                DemoLocation(
                    state=row["state"],
                    district=row["district"],
                    city=row["city"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                )
                for row in locations
            )
            total = 0
            for filename, module in FILES.items():
                reader = csv.DictReader(io.StringIO(bundle.read(filename).decode("utf-8-sig")))
                for row in reader:
                    payload = dict(row)
                    session.add(
                        DemoEnvironmentalRecord(
                            module=module,
                            state=row["state"],
                            district=row.get("district"),
                            city=row.get("city"),
                            latitude=number(row.get("latitude")),
                            longitude=number(row.get("longitude")),
                            observed_at=parse_datetime(row.get("observed_at") or row.get("sampled_at") or row.get("reporting_date")),
                            source=row["source"],
                            data_status="synthetic_demo",
                            is_real_measurement=False,
                            payload=json.dumps(payload),
                        )
                    )
                    total += 1
        session.commit()
        print(f"Imported {total} synthetic demo records and locations.")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import the EcoVision college demo dataset.")
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()
    import_bundle(args.zip_path)
