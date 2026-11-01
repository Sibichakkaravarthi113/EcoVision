from app.routers.health import router as health_router
from app.routers.locations import router as locations_router
from app.routers.overview import router as overview_router
from app.routers.air_quality import router as air_quality_router
from app.routers.water_quality import router as water_quality_router
from app.routers.green_coverage import router as green_coverage_router
from app.routers.waste_management import router as waste_management_router
from app.routers.noise_pollution import router as noise_pollution_router
from app.routers.traffic import router as traffic_router
from app.routers.industrial import router as industrial_router
from app.routers.climate import router as climate_router
from app.routers.chat import router as chat_router

__all__ = [
    "health_router",
    "locations_router",
    "overview_router",
    "air_quality_router",
    "water_quality_router",
    "green_coverage_router",
    "waste_management_router",
    "noise_pollution_router",
    "traffic_router",
    "industrial_router",
    "climate_router",
    "chat_router",
]
