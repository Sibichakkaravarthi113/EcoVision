import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path so app modules import properly
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import engine, SessionLocal, Base
import app.models  # Register all models with Base.metadata
from app.models.location import Location
from app.models.air_quality import AirQualityReading
from app.models.water_quality import WaterQualityReading
from app.models.green_coverage import GreenCoverage
from app.models.waste_management import WasteManagement
from app.models.noise_pollution import NoisePollution
from app.models.traffic import TrafficCongestion
from app.models.industrial import IndustrialActivity
from app.models.climate import ClimateReading

from scripts.generate_demo_data import generate_all_data


def parse_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return None


def main():
    print("Initializing EcoVision Database Rebuild...")
    print("Dropping existing tables and recreating schema...")

    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    dataset = generate_all_data()

    db = SessionLocal()
    counts = {}

    try:
        # 1. Locations
        print("Importing locations...")
        loc_objects = [
            Location(
                country=row.get("country", "India"),
                state=row["state"],
                district=row.get("district"),
                city=row.get("city"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
            )
            for row in dataset.get("locations", [])
        ]
        db.bulk_save_objects(loc_objects)
        db.commit()
        counts["locations"] = len(loc_objects)

        # 2. Air Quality
        print("Importing air quality demo records...")
        aq_objects = [
            AirQualityReading(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_demo"),
                is_demo=row.get("is_demo", True),
                parameter=row["parameter"],
                value=row["value"],
                unit=row["unit"],
                pollutant_category=row["pollutant_category"],
            )
            for row in dataset.get("air_quality", [])
        ]
        db.bulk_save_objects(aq_objects)
        db.commit()
        counts["air_quality"] = len(aq_objects)

        # 3. Water Quality
        print("Importing water quality records...")
        wq_objects = [
            WaterQualityReading(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_demo"),
                is_demo=row.get("is_demo", True),
                parameter=row["parameter"],
                value=row["value"],
                unit=row["unit"],
                station_code=row.get("station_code"),
            )
            for row in dataset.get("water_quality", [])
        ]
        db.bulk_save_objects(wq_objects)
        db.commit()
        counts["water_quality"] = len(wq_objects)

        # 4. Green Coverage
        print("Importing green coverage records...")
        gc_objects = [
            GreenCoverage(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_public"),
                is_demo=row.get("is_demo", False),
                district_name=row["district_name"],
                total_forest_area_sqkm=row["total_forest_area_sqkm"],
                very_dense_forest=row["very_dense_forest"],
                moderate_dense_forest=row["moderate_dense_forest"],
                open_forest=row["open_forest"],
                forest_cover_percent=row["forest_cover_percent"],
                geographic_area_sqkm=row["geographic_area_sqkm"],
                data_year=row["data_year"],
            )
            for row in dataset.get("green_coverage", [])
        ]
        db.bulk_save_objects(gc_objects)
        db.commit()
        counts["green_coverage"] = len(gc_objects)

        # 5. Waste Management
        print("Importing waste management records...")
        wm_objects = [
            WasteManagement(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_public"),
                is_demo=row.get("is_demo", False),
                waste_category=row["waste_category"],
                generated_tonnes_day=row["generated_tonnes_day"],
                collected_tonnes_day=row["collected_tonnes_day"],
                processed_tonnes_day=row["processed_tonnes_day"],
                recycling_percent=row["recycling_percent"],
                landfill_sites=row.get("landfill_sites"),
                reporting_year=row["reporting_year"],
            )
            for row in dataset.get("waste_management", [])
        ]
        db.bulk_save_objects(wm_objects)
        db.commit()
        counts["waste_management"] = len(wm_objects)

        # 6. Noise Pollution
        print("Importing noise pollution records...")
        np_objects = [
            NoisePollution(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_public"),
                is_demo=row.get("is_demo", False),
                location_type=row["location_type"],
                day_db=row["day_db"],
                night_db=row["night_db"],
                measurement_period=row["measurement_period"],
            )
            for row in dataset.get("noise_pollution", [])
        ]
        db.bulk_save_objects(np_objects)
        db.commit()
        counts["noise_pollution"] = len(np_objects)

        # 7. Traffic Congestion
        print("Importing traffic congestion records...")
        tr_objects = [
            TrafficCongestion(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_public"),
                is_demo=row.get("is_demo", False),
                road_name=row["road_name"],
                vehicle_count_hour=row.get("vehicle_count_hour"),
                avg_speed_kmh=row.get("avg_speed_kmh"),
                congestion_level=row["congestion_level"],
                peak_hour=row.get("peak_hour"),
            )
            for row in dataset.get("traffic", [])
        ]
        db.bulk_save_objects(tr_objects)
        db.commit()
        counts["traffic"] = len(tr_objects)

        # 8. Industrial Activity
        print("Importing industrial activity records...")
        ind_objects = [
            IndustrialActivity(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_public"),
                is_demo=row.get("is_demo", False),
                industry_type=row["industry_type"],
                industry_name=row["industry_name"],
                compliance_status=row["compliance_status"],
                emissions_indicator=row.get("emissions_indicator"),
                consent_to_operate=row.get("consent_to_operate"),
                reporting_year=row["reporting_year"],
            )
            for row in dataset.get("industrial", [])
        ]
        db.bulk_save_objects(ind_objects)
        db.commit()
        counts["industrial"] = len(ind_objects)

        # 9. Climate Readings
        print("Importing climate readings (historical + forecasts)...")
        cl_objects = [
            ClimateReading(
                state=row["state"],
                district=row.get("district"),
                city=row["city"],
                station_name=row.get("station_name"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                data_source=row["data_source"],
                observed_at=parse_dt(row.get("observed_at")),
                data_status=row.get("data_status", "synthetic_public"),
                is_demo=row.get("is_demo", False),
                temperature_c=row.get("temperature_c"),
                humidity_percent=row.get("humidity_percent"),
                rainfall_mm=row.get("rainfall_mm"),
                wind_speed_kmh=row.get("wind_speed_kmh"),
                weather_condition=row.get("weather_condition"),
                is_forecast=row.get("is_forecast", False),
                forecast_hour=row.get("forecast_hour"),
            )
            for row in dataset.get("climate", [])
        ]
        db.bulk_save_objects(cl_objects)
        db.commit()
        counts["climate"] = len(cl_objects)

        print("\n==========================================")
        print("DEMO AND BASELINE PUBLIC DATA IMPORT COMPLETED")
        print("==========================================")
        for table, count in counts.items():
            print(f" - {table:<20}: {count:>6} records imported")
        print("==========================================")

    except Exception as exc:
        db.rollback()
        print(f"Error during import_demo_data: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
