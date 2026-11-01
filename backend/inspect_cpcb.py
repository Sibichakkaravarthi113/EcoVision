
import json
from collections import Counter
from pathlib import Path

file_path = Path("data/cpcb_air_quality.json")

with file_path.open("r", encoding="utf-8") as file:
    data = json.load(file)

records = data.get("records", [])

print("Total records:", len(records))
print("States:", len(set(r.get("state") for r in records)))
print("Cities:", len(set(r.get("city") for r in records)))
print("Pollutants:", Counter(r.get("pollutant_id") for r in records))

missing_values = sum(
    1 for r in records
    if r.get("avg_value") in (None, "", "NA")
)

print("Missing average values:", missing_values)

print("\nSample record:")
print(json.dumps(records[0], indent=4))


print("\nPollutant value examples:")

for pollutant in sorted(set(r.get("pollutant_id") for r in records)):
    examples = [
        r.get("avg_value")
        for r in records
        if r.get("pollutant_id") == pollutant
        and r.get("avg_value") not in (None, "", "NA")
    ]

    print(f"{pollutant}: {examples[:5]}")

