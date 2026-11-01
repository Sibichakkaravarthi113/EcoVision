
import os
import httpx

CPCB_API_URL = (
    "https://api.data.gov.in/resource/"
    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
)


async def fetch_air_quality(state=None, city=None):
    api_key = os.getenv("DATA_GOV_IN_API_KEY")

    if not api_key:
        raise ValueError("Data.gov.in API key is missing.")

    params = {
        "api-key": api_key,
        "format": "json",
        "offset": 0,
        "limit": 1000,
    }

    if state:
        params["filters[state]"] = state

    if city:
        params["filters[city]"] = city

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.get(CPCB_API_URL, params=params)

        if response.is_error:
            raise RuntimeError(
                f"Data.gov.in returned HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )
        data = response.json()
