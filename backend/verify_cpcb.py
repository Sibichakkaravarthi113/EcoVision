
from sqlalchemy import func

from app.database import SessionLocal
from app.models.environmental_reading import EnvironmentalReading


db = SessionLocal()

try:
    # 1. Overall database count
    total = db.query(EnvironmentalReading).count()

    cpcb_total = (
        db.query(EnvironmentalReading)
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in"
        )
        .count()
    )

    print("========== DATABASE SUMMARY ==========")
    print("Total database readings:", total)
    print("CPCB readings:", cpcb_total)

    # 2. State-wise CPCB records
    print("\n========== STATE-WISE CPCB RECORDS ==========")

    results = (
        db.query(
            EnvironmentalReading.state,
            func.count(EnvironmentalReading.id)
        )
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in"
        )
        .group_by(EnvironmentalReading.state)
        .order_by(EnvironmentalReading.state)
        .all()
    )

    for state, count in results:
        print(f"{state}: {count}")

    # 3. Pollutant-wise CPCB records
    print("\n========== POLLUTANT-WISE CPCB RECORDS ==========")

    results = (
        db.query(
            EnvironmentalReading.parameter,
            func.count(EnvironmentalReading.id)
        )
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in"
        )
        .group_by(EnvironmentalReading.parameter)
        .order_by(EnvironmentalReading.parameter)
        .all()
    )

    for pollutant, count in results:
        print(f"{pollutant}: {count}")

    # 4. Inspect all Chennai pollutant records
    print("\n========== CHENNAI POLLUTANT RECORDS ==========")

    chennai_records = (
        db.query(EnvironmentalReading)
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in",
            EnvironmentalReading.city.ilike("Chennai")
        )
        .order_by(
            EnvironmentalReading.station,
            EnvironmentalReading.parameter
        )
        .all()
    )

    print("Total Chennai records:", len(chennai_records))

    for row in chennai_records:
        print(
            f"Station: {row.station} | "
            f"Pollutant: {row.parameter} | "
            f"Value: {row.value} {row.unit} | "
            f"Timestamp: {row.observed_at}"
        )

    # 5. Specifically inspect Chennai PM2.5
    print("\n========== CHENNAI PM2.5 RECORDS ==========")

    pm25_records = (
        db.query(EnvironmentalReading)
        .filter(
            EnvironmentalReading.source == "CPCB / data.gov.in",
            EnvironmentalReading.city.ilike("Chennai"),
            EnvironmentalReading.parameter.ilike("PM2.5")
        )
        .all()
    )

    print("Chennai PM2.5 count:", len(pm25_records))

    for row in pm25_records:
        print(
            f"Station: {row.station} | "
            f"Value: {row.value} {row.unit} | "
            f"State: {row.state} | "
            f"City: {row.city}"
        )

    print("\n========== VERIFICATION COMPLETED ==========")

finally:
    db.close()
