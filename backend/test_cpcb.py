
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DATA_GOV_IN_API_KEY")

if not api_key:
    print("API key not found in .env")
    raise SystemExit(1)

url = (
    "https://api.data.gov.in/resource/"
    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
)

params = {
    "api-key": api_key,
    "format": "json",
    "limit": 5
}

try:
    response = httpx.get(url, params=params, timeout=60)

    print("HTTP Status:", response.status_code)
    print("Response:")
    print(response.text[:1500])

except httpx.RequestError as error:
    print("Connection Error:", repr(error))
