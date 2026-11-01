import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Fixed random seed for complete reproducibility
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "synthetic_demo_data.json"

ANCHOR_DATE = datetime(2026, 11, 1, 12, 0, 0)

# 12 Demo Cities
DEMO_CITIES = [
    {"city": "Chennai", "district": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "region": "coastal_south"},
    {"city": "Madurai", "district": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lon": 78.1198, "region": "south"},
    {"city": "Coimbatore", "district": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lon": 76.9558, "region": "south"},
    {"city": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "region": "south"},
    {"city": "Mysuru", "district": "Mysuru", "state": "Karnataka", "lat": 12.2958, "lon": 76.6394, "region": "south"},
    {"city": "Kochi", "district": "Ernakulam", "state": "Kerala", "lat": 9.9312, "lon": 76.2673, "region": "coastal_south"},
    {"city": "Thiruvananthapuram", "district": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lon": 76.9366, "region": "coastal_south"},
    {"city": "Mumbai", "district": "Mumbai City", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "region": "coastal_west"},
    {"city": "Pune", "district": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567, "region": "west"},
    {"city": "New Delhi", "district": "New Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090, "region": "north"},
    {"city": "Hyderabad", "district": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "region": "south"},
    {"city": "Ahmedabad", "district": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714, "region": "west"},
]

# Public Data Cities covering all Indian states/UTs (>50 cities)
PUBLIC_CITIES = [
    # Tamil Nadu
    {"city": "Salem", "district": "Salem", "state": "Tamil Nadu", "lat": 11.6643, "lon": 78.1460, "region": "south"},
    {"city": "Tiruchirappalli", "district": "Tiruchirappalli", "state": "Tamil Nadu", "lat": 10.7905, "lon": 78.7047, "region": "south"},
    {"city": "Tirunelveli", "district": "Tirunelveli", "state": "Tamil Nadu", "lat": 8.7139, "lon": 77.7567, "region": "south"},
    {"city": "Erode", "district": "Erode", "state": "Tamil Nadu", "lat": 11.3410, "lon": 77.7172, "region": "south"},
    {"city": "Vellore", "district": "Vellore", "state": "Tamil Nadu", "lat": 12.9165, "lon": 79.1325, "region": "south"},
    # Karnataka
    {"city": "Hubballi", "district": "Dharwad", "state": "Karnataka", "lat": 15.3647, "lon": 75.1240, "region": "south"},
    {"city": "Mangaluru", "district": "Dakshina Kannada", "state": "Karnataka", "lat": 12.9141, "lon": 74.8560, "region": "coastal_south"},
    {"city": "Belagavi", "district": "Belagavi", "state": "Karnataka", "lat": 15.8497, "lon": 74.4977, "region": "south"},
    # Kerala
    {"city": "Kozhikode", "district": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lon": 75.7804, "region": "coastal_south"},
    {"city": "Thrissur", "district": "Thrissur", "state": "Kerala", "lat": 10.5276, "lon": 76.2144, "region": "south"},
    {"city": "Kollam", "district": "Kollam", "state": "Kerala", "lat": 8.8932, "lon": 76.6141, "region": "coastal_south"},
    # Maharashtra
    {"city": "Nagpur", "district": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lon": 79.0882, "region": "central"},
    {"city": "Nashik", "district": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898, "region": "west"},
    {"city": "Aurangabad", "district": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lon": 75.3433, "region": "west"},
    {"city": "Thane", "district": "Thane", "state": "Maharashtra", "lat": 19.2183, "lon": 72.9781, "region": "coastal_west"},
    # Telangana
    {"city": "Warangal", "district": "Warangal", "state": "Telangana", "lat": 17.9689, "lon": 79.5941, "region": "south"},
    {"city": "Nizamabad", "district": "Nizamabad", "state": "Telangana", "lat": 18.6725, "lon": 78.0941, "region": "south"},
    # Andhra Pradesh
    {"city": "Visakhapatnam", "district": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185, "region": "coastal_east"},
    {"city": "Vijayawada", "district": "NTR", "state": "Andhra Pradesh", "lat": 16.5062, "lon": 80.6480, "region": "south"},
    {"city": "Guntur", "district": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lon": 80.4365, "region": "south"},
    {"city": "Nellore", "district": "SPSR Nellore", "state": "Andhra Pradesh", "lat": 14.4426, "lon": 79.9865, "region": "coastal_south"},
    {"city": "Tirupati", "district": "Tirupati", "state": "Andhra Pradesh", "lat": 13.6288, "lon": 79.4192, "region": "south"},
    # Gujarat
    {"city": "Surat", "district": "Surat", "state": "Gujarat", "lat": 21.1702, "lon": 72.8311, "region": "coastal_west"},
    {"city": "Vadodara", "district": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lon": 73.1812, "region": "west"},
    {"city": "Rajkot", "district": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lon": 70.8022, "region": "west"},
    # Rajasthan
    {"city": "Jaipur", "district": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873, "region": "north"},
    {"city": "Jodhpur", "district": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lon": 73.0243, "region": "north"},
    {"city": "Udaipur", "district": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lon": 73.7125, "region": "north"},
    {"city": "Kota", "district": "Kota", "state": "Rajasthan", "lat": 25.2138, "lon": 75.8648, "region": "north"},
    # Uttar Pradesh
    {"city": "Lucknow", "district": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462, "region": "north"},
    {"city": "Kanpur", "district": "Kanpur Nagar", "state": "Uttar Pradesh", "lat": 26.4499, "lon": 80.3319, "region": "north"},
    {"city": "Varanasi", "district": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739, "region": "north"},
    {"city": "Agra", "district": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lon": 78.0081, "region": "north"},
    {"city": "Prayagraj", "district": "Prayagraj", "state": "Uttar Pradesh", "lat": 25.4358, "lon": 81.8463, "region": "north"},
    {"city": "Noida", "district": "Gautam Buddha Nagar", "state": "Uttar Pradesh", "lat": 28.5355, "lon": 77.3910, "region": "north"},
    # West Bengal
    {"city": "Kolkata", "district": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639, "region": "east"},
    {"city": "Howrah", "district": "Howrah", "state": "West Bengal", "lat": 22.5958, "lon": 88.2636, "region": "east"},
    {"city": "Durgapur", "district": "Paschim Bardhaman", "state": "West Bengal", "lat": 23.5204, "lon": 87.3119, "region": "east"},
    {"city": "Siliguri", "district": "Darjeeling", "state": "West Bengal", "lat": 26.7271, "lon": 88.3953, "region": "east"},
    # Madhya Pradesh
    {"city": "Bhopal", "district": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126, "region": "central"},
    {"city": "Indore", "district": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577, "region": "central"},
    {"city": "Jabalpur", "district": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lon": 79.9864, "region": "central"},
    {"city": "Gwalior", "district": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lon": 78.1828, "region": "central"},
    # Bihar
    {"city": "Patna", "district": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376, "region": "north"},
    {"city": "Gaya", "district": "Gaya", "state": "Bihar", "lat": 24.7914, "lon": 85.0002, "region": "north"},
    {"city": "Bhagalpur", "district": "Bhagalpur", "state": "Bihar", "lat": 25.2425, "lon": 86.9842, "region": "north"},
    {"city": "Muzaffarpur", "district": "Muzaffarpur", "state": "Bihar", "lat": 26.1209, "lon": 85.3647, "region": "north"},
    # Odisha
    {"city": "Bhubaneswar", "district": "Khurda", "state": "Odisha", "lat": 20.2961, "lon": 85.8245, "region": "coastal_east"},
    {"city": "Cuttack", "district": "Cuttack", "state": "Odisha", "lat": 20.4625, "lon": 85.8828, "region": "east"},
    {"city": "Rourkela", "district": "Sundargarh", "state": "Odisha", "lat": 22.2604, "lon": 84.8536, "region": "east"},
    # Punjab & Haryana & Chandigarh
    {"city": "Ludhiana", "district": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lon": 75.8573, "region": "north"},
    {"city": "Amritsar", "district": "Amritsar", "state": "Punjab", "lat": 31.6340, "lon": 74.8723, "region": "north"},
    {"city": "Jalandhar", "district": "Jalandhar", "state": "Punjab", "lat": 31.3260, "lon": 75.5762, "region": "north"},
    {"city": "Gurugram", "district": "Gurugram", "state": "Haryana", "lat": 28.4595, "lon": 77.0266, "region": "north"},
    {"city": "Faridabad", "district": "Faridabad", "state": "Haryana", "lat": 28.4089, "lon": 77.3178, "region": "north"},
    {"city": "Panipat", "district": "Panipat", "state": "Haryana", "lat": 29.3909, "lon": 76.9635, "region": "north"},
    {"city": "Chandigarh", "district": "Chandigarh", "state": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "region": "north"},
    # Assam & Northeast
    {"city": "Guwahati", "district": "Kamrup Metropolitan", "state": "Assam", "lat": 26.1445, "lon": 91.7362, "region": "northeast"},
    {"city": "Silchar", "district": "Cachar", "state": "Assam", "lat": 24.8333, "lon": 92.7789, "region": "northeast"},
    {"city": "Dibrugarh", "district": "Dibrugarh", "state": "Assam", "lat": 27.4728, "lon": 94.9120, "region": "northeast"},
    {"city": "Shillong", "district": "East Khasi Hills", "state": "Meghalaya", "lat": 25.5788, "lon": 91.8933, "region": "northeast"},
    {"city": "Aizawl", "district": "Aizawl", "state": "Mizoram", "lat": 23.7271, "lon": 92.7176, "region": "northeast"},
    {"city": "Imphal", "district": "Imphal West", "state": "Manipur", "lat": 24.8170, "lon": 93.9368, "region": "northeast"},
    {"city": "Agartala", "district": "West Tripura", "state": "Tripura", "lat": 23.8315, "lon": 91.2868, "region": "northeast"},
    {"city": "Kohima", "district": "Kohima", "state": "Nagaland", "lat": 25.6751, "lon": 94.1086, "region": "northeast"},
    {"city": "Gangtok", "district": "East Sikkim", "state": "Sikkim", "lat": 27.3389, "lon": 88.6065, "region": "northeast"},
    {"city": "Itanagar", "district": "Papum Pare", "state": "Arunachal Pradesh", "lat": 27.0844, "lon": 93.6053, "region": "northeast"},
    # Hill States
    {"city": "Shimla", "district": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734, "region": "north"},
    {"city": "Dharamshala", "district": "Kangra", "state": "Himachal Pradesh", "lat": 32.2190, "lon": 76.3234, "region": "north"},
    {"city": "Dehradun", "district": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lon": 78.0322, "region": "north"},
    {"city": "Haridwar", "district": "Haridwar", "state": "Uttarakhand", "lat": 29.9457, "lon": 78.1642, "region": "north"},
    # Goa
    {"city": "Panaji", "district": "North Goa", "state": "Goa", "lat": 15.4909, "lon": 73.8278, "region": "coastal_west"},
    {"city": "Margao", "district": "South Goa", "state": "Goa", "lat": 15.2832, "lon": 73.9862, "region": "coastal_west"},
    # Jharkhand & Chhattisgarh
    {"city": "Ranchi", "district": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lon": 85.3096, "region": "east"},
    {"city": "Jamshedpur", "district": "East Singhbhum", "state": "Jharkhand", "lat": 22.8046, "lon": 86.2029, "region": "east"},
    {"city": "Dhanbad", "district": "Dhanbad", "state": "Jharkhand", "lat": 23.7957, "lon": 86.4304, "region": "east"},
    {"city": "Raipur", "district": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lon": 81.6296, "region": "central"},
    {"city": "Bhilai", "district": "Durg", "state": "Chhattisgarh", "lat": 21.2144, "lon": 81.3784, "region": "central"},
    {"city": "Bilaspur", "district": "Bilaspur", "state": "Chhattisgarh", "lat": 22.0797, "lon": 82.1409, "region": "central"},
    # Jammu and Kashmir
    {"city": "Srinagar", "district": "Srinagar", "state": "Jammu and Kashmir", "lat": 34.0837, "lon": 74.7973, "region": "north"},
    {"city": "Jammu", "district": "Jammu", "state": "Jammu and Kashmir", "lat": 32.7266, "lon": 74.8570, "region": "north"},
]

# State Forest Coverage reference data (FSI 2023 approx percent)
STATE_FOREST_PERCENT = {
    "Kerala": 54.4,
    "Mizoram": 84.5,
    "Himachal Pradesh": 27.7,
    "Tamil Nadu": 20.3,
    "Maharashtra": 20.1,
    "Delhi": 20.0,
    "Karnataka": 20.1,
    "Goa": 60.4,
    "Uttarakhand": 45.4,
    "Assam": 36.1,
    "Meghalaya": 76.0,
    "Manipur": 74.3,
    "Nagaland": 73.9,
    "Arunachal Pradesh": 79.3,
    "Tripura": 73.6,
    "Sikkim": 47.1,
    "Madhya Pradesh": 25.1,
    "Chhattisgarh": 41.1,
    "Odisha": 33.5,
    "Andhra Pradesh": 17.8,
    "Telangana": 18.3,
    "Gujarat": 7.6,
    "Rajasthan": 4.9,
    "Uttar Pradesh": 6.1,
    "Bihar": 7.8,
    "West Bengal": 19.0,
    "Punjab": 3.7,
    "Haryana": 3.6,
    "Jharkhand": 29.8,
    "Jammu and Kashmir": 39.1,
    "Chandigarh": 40.0,
}


def get_aqi_category(parameter: str, value: float) -> str:
    """Categorizes pollutant reading based on CPCB AQI standards."""
    if parameter == "PM2.5":
        if value <= 30: return "Good"
        elif value <= 60: return "Satisfactory"
        elif value <= 90: return "Moderate"
        elif value <= 120: return "Poor"
        elif value <= 250: return "Very Poor"
        return "Severe"
    elif parameter == "PM10":
        if value <= 50: return "Good"
        elif value <= 100: return "Satisfactory"
        elif value <= 250: return "Moderate"
        elif value <= 350: return "Poor"
        elif value <= 430: return "Very Poor"
        return "Severe"
    elif parameter == "NO2":
        if value <= 40: return "Good"
        elif value <= 80: return "Satisfactory"
        elif value <= 180: return "Moderate"
        elif value <= 280: return "Poor"
        return "Very Poor"
    elif parameter == "SO2":
        if value <= 40: return "Good"
        elif value <= 80: return "Satisfactory"
        elif value <= 380: return "Moderate"
        return "Poor"
    elif parameter == "CO":
        if value <= 1.0: return "Good"
        elif value <= 2.0: return "Satisfactory"
        elif value <= 10.0: return "Moderate"
        return "Poor"
    elif parameter == "OZONE":
        if value <= 50: return "Good"
        elif value <= 100: return "Satisfactory"
        elif value <= 168: return "Moderate"
        return "Poor"
    elif parameter == "NH3":
        if value <= 200: return "Good"
        elif value <= 400: return "Satisfactory"
        return "Moderate"
    return "Moderate"


def generate_air_quality(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic air quality readings."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    for city_meta in cities:
        c_name = city_meta["city"]
        num_stations = random.randint(3, 8)
        
        # Region bias for PM2.5 / PM10
        is_delhi_mumbai = c_name in ["New Delhi", "Mumbai"]
        is_kerala = city_meta["state"] == "Kerala"

        for st_idx in range(1, num_stations + 1):
            station_name = f"{c_name} Station {st_idx} - EnvNet"
            st_lat = city_meta["lat"] + random.uniform(-0.05, 0.05)
            st_lon = city_meta["lon"] + random.uniform(-0.05, 0.05)
            obs_time = ANCHOR_DATE - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))

            pollutant_configs = [
                ("PM2.5", "µg/m³", (90, 180) if is_delhi_mumbai else ((15, 45) if is_kerala else (35, 120))),
                ("PM10", "µg/m³", (140, 250) if is_delhi_mumbai else ((25, 75) if is_kerala else (50, 180))),
                ("NO2", "µg/m³", (25, 80) if is_delhi_mumbai else (5, 50)),
                ("SO2", "µg/m³", (5, 40)),
                ("OZONE", "µg/m³", (20, 100)),
                ("NH3", "µg/m³", (1, 30)),
                ("CO", "mg/m³", (0.5, 4.8) if is_delhi_mumbai else (0.1, 2.5)),
            ]

            for param, unit, (low, high) in pollutant_configs:
                val = round(random.uniform(low, high), 2)
                cat = get_aqi_category(param, val)

                records.append({
                    "state": city_meta["state"],
                    "district": city_meta["district"],
                    "city": c_name,
                    "station_name": station_name,
                    "latitude": round(st_lat, 6),
                    "longitude": round(st_lon, 6),
                    "data_source": source,
                    "observed_at": obs_time.isoformat(),
                    "data_status": status,
                    "is_demo": is_demo,
                    "parameter": param,
                    "value": val,
                    "unit": unit,
                    "pollutant_category": cat,
                })
    return records


def generate_water_quality(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic water quality readings."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    water_parameters = [
        ("Potential of Hydrogen (pH)", "pH", 6.5, 8.5),
        ("Dissolved oxygen (mg/L)", "mg/L", 2.0, 12.0),
        ("Total Dissolved Solids (mg/L)", "mg/L", 100.0, 2000.0),
        ("Biochemical Oxygen Demand (BOD)", "mg/L", 1.0, 30.0),
        ("Nitrate (mg/L)", "mg/L", 1.0, 50.0),
        ("Total Coliform (MPN/100mL)", "MPN/100mL", 5.0, 4800.0),
    ]

    for city_meta in cities:
        c_name = city_meta["city"]
        num_stations = random.randint(2, 5)

        for s_idx in range(1, num_stations + 1):
            st_name = f"{c_name} Water Monitoring Point {s_idx}"
            st_code = f"WQP-{c_name[:3].upper()}-{s_idx:02d}"
            st_lat = city_meta["lat"] + random.uniform(-0.04, 0.04)
            st_lon = city_meta["lon"] + random.uniform(-0.04, 0.04)
            obs_time = ANCHOR_DATE - timedelta(days=random.randint(1, 60), hours=random.randint(8, 16))

            for param_name, unit, low, high in water_parameters:
                val = round(random.uniform(low, high), 2)
                records.append({
                    "state": city_meta["state"],
                    "district": city_meta["district"],
                    "city": c_name,
                    "station_name": st_name,
                    "latitude": round(st_lat, 6),
                    "longitude": round(st_lon, 6),
                    "data_source": source,
                    "observed_at": obs_time.isoformat(),
                    "data_status": status,
                    "is_demo": is_demo,
                    "parameter": param_name,
                    "value": val,
                    "unit": unit,
                    "station_code": st_code,
                })
    return records


def generate_green_coverage(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic green / forest coverage records."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    seen_districts = set()

    for city_meta in cities:
        dist_name = city_meta["district"]
        st_name = city_meta["state"]
        key = (st_name, dist_name)
        if key in seen_districts:
            continue
        seen_districts.add(key)

        base_pct = STATE_FOREST_PERCENT.get(st_name, 22.0)
        dist_pct = round(max(2.0, min(95.0, base_pct + random.uniform(-6.0, 6.0))), 2)

        geo_area = round(random.uniform(2000.0, 8000.0), 2)
        total_forest = round(geo_area * (dist_pct / 100.0), 2)
        very_dense = round(total_forest * random.uniform(0.15, 0.35), 2)
        mod_dense = round(total_forest * random.uniform(0.35, 0.55), 2)
        open_forest = round(max(0.0, total_forest - (very_dense + mod_dense)), 2)

        records.append({
            "state": st_name,
            "district": dist_name,
            "city": city_meta["city"],
            "station_name": f"{dist_name} FSI Assessment Unit",
            "latitude": round(city_meta["lat"], 6),
            "longitude": round(city_meta["lon"], 6),
            "data_source": source,
            "observed_at": datetime(2023, 12, 31).isoformat(),
            "data_status": status,
            "is_demo": is_demo,
            "district_name": dist_name,
            "total_forest_area_sqkm": total_forest,
            "very_dense_forest": very_dense,
            "moderate_dense_forest": mod_dense,
            "open_forest": open_forest,
            "forest_cover_percent": dist_pct,
            "geographic_area_sqkm": geo_area,
            "data_year": 2023,
        })
    return records


def generate_waste_management(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic municipal waste management data."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    for city_meta in cities:
        c_name = city_meta["city"]
        if c_name == "New Delhi":
            gen = round(random.uniform(9500, 11500), 1)
        elif c_name == "Mumbai":
            gen = round(random.uniform(6500, 8000), 1)
        elif c_name == "Chennai":
            gen = round(random.uniform(4800, 5600), 1)
        elif c_name in ["Bengaluru", "Hyderabad", "Kolkata", "Ahmedabad", "Pune"]:
            gen = round(random.uniform(3500, 5000), 1)
        else:
            gen = round(random.uniform(150, 1800), 1)

        coll_eff = random.uniform(0.65, 0.95)
        coll = round(gen * coll_eff, 1)
        proc_eff = random.uniform(0.35, 0.85)
        proc = round(coll * proc_eff, 1)
        rec_pct = round(random.uniform(8.0, 38.0), 1)
        landfills = random.randint(1, 4)

        obs_time = ANCHOR_DATE - timedelta(days=random.randint(1, 45))

        records.append({
            "state": city_meta["state"],
            "district": city_meta["district"],
            "city": c_name,
            "station_name": f"{c_name} Municipal Corporation SWM Division",
            "latitude": round(city_meta["lat"], 6),
            "longitude": round(city_meta["lon"], 6),
            "data_source": source,
            "observed_at": obs_time.isoformat(),
            "data_status": status,
            "is_demo": is_demo,
            "waste_category": "Municipal Solid Waste (MSW)",
            "generated_tonnes_day": gen,
            "collected_tonnes_day": coll,
            "processed_tonnes_day": proc,
            "recycling_percent": rec_pct,
            "landfill_sites": landfills,
            "reporting_year": 2026,
        })
    return records


def generate_noise_pollution(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic ambient noise monitoring records."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    zones = [
        ("residential", (52.0, 74.0), (41.0, 63.0)),
        ("commercial", (61.0, 79.0), (51.0, 68.0)),
        ("industrial", (71.0, 89.0), (61.0, 78.0)),
        ("silence", (46.0, 58.0), (36.0, 48.0)),
    ]

    for city_meta in cities:
        c_name = city_meta["city"]

        for zone_type, (day_min, day_max), (night_min, night_max) in zones:
            st_lat = city_meta["lat"] + random.uniform(-0.03, 0.03)
            st_lon = city_meta["lon"] + random.uniform(-0.03, 0.03)
            day_db = round(random.uniform(day_min, day_max), 1)
            night_db = round(random.uniform(night_min, night_max), 1)
            obs_time = ANCHOR_DATE - timedelta(days=random.randint(1, 30))

            records.append({
                "state": city_meta["state"],
                "district": city_meta["district"],
                "city": c_name,
                "station_name": f"{c_name} {zone_type.capitalize()} Noise Station",
                "latitude": round(st_lat, 6),
                "longitude": round(st_lon, 6),
                "data_source": source,
                "observed_at": obs_time.isoformat(),
                "data_status": status,
                "is_demo": is_demo,
                "location_type": zone_type,
                "day_db": day_db,
                "night_db": night_db,
                "measurement_period": "Leq 24-hr Ambient",
            })
    return records


def generate_traffic(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic traffic congestion monitoring records."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    road_prefixes = [
        "Ring Road", "MG Road", "Airport Arterial Road", "Anna Salai Express Corridor",
        "Outer Bypass Highway", "Station Road", "IT Corridor Boulevard", "Industrial Link Way"
    ]

    for city_meta in cities:
        c_name = city_meta["city"]
        num_roads = random.randint(3, 6)

        for r_idx in range(num_roads):
            road_name = f"{c_name} {road_prefixes[r_idx % len(road_prefixes)]}"
            spd = round(random.uniform(12.0, 58.0), 1)
            veh = random.randint(550, 4900)

            if spd < 20.0:
                c_level = "severe"
            elif spd < 30.0:
                c_level = "high"
            elif spd < 45.0:
                c_level = "moderate"
            else:
                c_level = "low"

            peak = random.choice(["08:00-10:00", "17:00-20:00", "12:00-14:00"])
            obs_time = ANCHOR_DATE - timedelta(hours=random.randint(1, 48))

            records.append({
                "state": city_meta["state"],
                "district": city_meta["district"],
                "city": c_name,
                "station_name": f"{road_name} Sensor Unit",
                "latitude": round(city_meta["lat"] + random.uniform(-0.03, 0.03), 6),
                "longitude": round(city_meta["lon"] + random.uniform(-0.03, 0.03), 6),
                "data_source": source,
                "observed_at": obs_time.isoformat(),
                "data_status": status,
                "is_demo": is_demo,
                "road_name": road_name,
                "vehicle_count_hour": veh,
                "avg_speed_kmh": spd,
                "congestion_level": c_level,
                "peak_hour": peak,
            })
    return records


def generate_industrial(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic industrial facility compliance records."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    industry_types = [
        "Cement", "Steel", "Thermal Power", "Textile", "Chemical",
        "Pharmaceutical", "Auto", "IT/Software", "Food Processing", "Paper"
    ]

    for city_meta in cities:
        c_name = city_meta["city"]
        num_ind = random.randint(5, 15)

        for i_idx in range(1, num_ind + 1):
            ind_type = random.choice(industry_types)
            ind_name = f"{c_name} {ind_type} Works Unit {i_idx}"
            comp = random.choices(["compliant", "non_compliant", "under_observation"], weights=[0.70, 0.15, 0.15])[0]
            cto = comp != "non_compliant"
            indicator = f"{ind_type} Particulate & Stack Emissions"
            obs_time = ANCHOR_DATE - timedelta(days=random.randint(5, 75))

            records.append({
                "state": city_meta["state"],
                "district": city_meta["district"],
                "city": c_name,
                "station_name": f"{ind_name} Stack Monitor",
                "latitude": round(city_meta["lat"] + random.uniform(-0.05, 0.05), 6),
                "longitude": round(city_meta["lon"] + random.uniform(-0.05, 0.05), 6),
                "data_source": source,
                "observed_at": obs_time.isoformat(),
                "data_status": status,
                "is_demo": is_demo,
                "industry_type": ind_type,
                "industry_name": ind_name,
                "compliance_status": comp,
                "emissions_indicator": indicator,
                "consent_to_operate": cto,
                "reporting_year": 2026,
            })
    return records


def generate_climate(cities: List[Dict[str, Any]], is_demo: bool) -> List[Dict[str, Any]]:
    """Generates synthetic historical and forecast climate observations."""
    records = []
    status = "synthetic_demo" if is_demo else "synthetic_public"
    source = "EcoVision college demonstration dataset" if is_demo else "EcoVision synthetic public data"

    weather_conditions = ["Clear", "Partly Cloudy", "Hazy", "Overcast", "Light Rain", "Sunny"]

    for city_meta in cities:
        c_name = city_meta["city"]
        region = city_meta.get("region", "south")

        # Regional temperature base for November
        if region == "north":
            base_temp, hum_base = (22.0, 50.0)
        elif region == "northeast":
            base_temp, hum_base = (19.0, 75.0)
        elif "coastal" in region:
            base_temp, hum_base = (29.0, 80.0)
        else:
            base_temp, hum_base = (28.0, 60.0)

        # 1. Historical readings: Daily for past 30 days
        for day_ago in range(30, 0, -1):
            obs_time = ANCHOR_DATE - timedelta(days=day_ago)
            temp = round(base_temp + random.uniform(-4.0, 4.0), 1)
            hum = round(max(20.0, min(99.0, hum_base + random.uniform(-15.0, 15.0))), 1)
            rain = round(random.choice([0.0, 0.0, 0.0, 2.5, 8.0, 15.4]), 1)
            wind = round(random.uniform(5.0, 25.0), 1)
            cond = random.choice(weather_conditions) if rain == 0.0 else "Rain"

            records.append({
                "state": city_meta["state"],
                "district": city_meta["district"],
                "city": c_name,
                "station_name": f"{c_name} Regional Meteorological Center",
                "latitude": round(city_meta["lat"], 6),
                "longitude": round(city_meta["lon"], 6),
                "data_source": source,
                "observed_at": obs_time.isoformat(),
                "data_status": status,
                "is_demo": is_demo,
                "temperature_c": temp,
                "humidity_percent": hum,
                "rainfall_mm": rain,
                "wind_speed_kmh": wind,
                "weather_condition": cond,
                "is_forecast": False,
                "forecast_hour": None,
            })

        # 2. Hourly forecast for next 72 hours
        for f_hour in range(1, 73):
            f_time = ANCHOR_DATE + timedelta(hours=f_hour)
            # Diurnal temperature oscillation
            hour_of_day = f_time.hour
            diurnal_offset = 5.0 * ((12 - abs(hour_of_day - 14)) / 12)
            f_temp = round(base_temp + diurnal_offset + random.uniform(-1.5, 1.5), 1)
            f_hum = round(max(30.0, min(95.0, hum_base - diurnal_offset * 1.5 + random.uniform(-5.0, 5.0))), 1)
            f_rain = round(random.choice([0.0, 0.0, 0.0, 0.0, 1.2, 4.5]), 1)
            f_wind = round(random.uniform(8.0, 22.0), 1)
            f_cond = "Rain" if f_rain > 0 else ("Clear" if hour_of_day < 6 or hour_of_day > 18 else "Sunny")

            records.append({
                "state": city_meta["state"],
                "district": city_meta["district"],
                "city": c_name,
                "station_name": f"{c_name} Regional Meteorological Center",
                "latitude": round(city_meta["lat"], 6),
                "longitude": round(city_meta["lon"], 6),
                "data_source": source,
                "observed_at": f_time.isoformat(),
                "data_status": status,
                "is_demo": is_demo,
                "temperature_c": f_temp,
                "humidity_percent": f_hum,
                "rainfall_mm": f_rain,
                "wind_speed_kmh": f_wind,
                "weather_condition": f_cond,
                "is_forecast": True,
                "forecast_hour": f_hour,
            })
    return records


def generate_locations(demo_cities: List[Dict[str, Any]], public_cities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds a comprehensive list of unique Indian locations."""
    unique_map = {}
    for c in demo_cities + public_cities:
        key = (c["state"], c["city"])
        if key not in unique_map:
            unique_map[key] = {
                "country": "India",
                "state": c["state"],
                "district": c.get("district"),
                "city": c["city"],
                "latitude": round(c["lat"], 6),
                "longitude": round(c["lon"], 6),
            }
    return list(unique_map.values())


def generate_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """Generates all synthetic data across demo and public cities."""
    print("Generating synthetic data for EcoVision (seed=42)...")

    # 1. Air Quality (demo only, CPCB handles public)
    aq_demo = generate_air_quality(DEMO_CITIES, is_demo=True)

    # 2. Water Quality (demo + public beyond TN)
    wq_demo = generate_water_quality(DEMO_CITIES, is_demo=True)
    non_tn_public_cities = [c for c in PUBLIC_CITIES if c["state"] != "Tamil Nadu"]
    wq_public = generate_water_quality(non_tn_public_cities, is_demo=False)

    # 3. Green Coverage (demo + public)
    gc_demo = generate_green_coverage(DEMO_CITIES, is_demo=True)
    gc_public = generate_green_coverage(PUBLIC_CITIES, is_demo=False)

    # 4. Waste Management (demo + public)
    wm_demo = generate_waste_management(DEMO_CITIES, is_demo=True)
    wm_public = generate_waste_management(PUBLIC_CITIES, is_demo=False)

    # 5. Noise Pollution (demo + public)
    np_demo = generate_noise_pollution(DEMO_CITIES, is_demo=True)
    np_public = generate_noise_pollution(PUBLIC_CITIES, is_demo=False)

    # 6. Traffic Congestion (demo + public)
    tr_demo = generate_traffic(DEMO_CITIES, is_demo=True)
    tr_public = generate_traffic(PUBLIC_CITIES, is_demo=False)

    # 7. Industrial Activity (demo + public)
    ind_demo = generate_industrial(DEMO_CITIES, is_demo=True)
    ind_public = generate_industrial(PUBLIC_CITIES, is_demo=False)

    # 8. Climate Readings (demo + public)
    cl_demo = generate_climate(DEMO_CITIES, is_demo=True)
    cl_public = generate_climate(PUBLIC_CITIES, is_demo=False)

    # 9. Locations
    locations = generate_locations(DEMO_CITIES, PUBLIC_CITIES)

    dataset = {
        "locations": locations,
        "air_quality": aq_demo,
        "water_quality": wq_demo + wq_public,
        "green_coverage": gc_demo + gc_public,
        "waste_management": wm_demo + wm_public,
        "noise_pollution": np_demo + np_public,
        "traffic": tr_demo + tr_public,
        "industrial": ind_demo + ind_public,
        "climate": cl_demo + cl_public,
    }

    return dataset


def main():
    dataset = generate_all_data()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print("\n=== DEMO DATA GENERATION SUMMARY ===")
    for k, v in dataset.items():
        print(f" - {k}: {len(v)} records")
    print(f"Data saved to: {OUTPUT_FILE}")
    print("=====================================")


if __name__ == "__main__":
    main()
