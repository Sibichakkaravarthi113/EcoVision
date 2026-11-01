from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.database import engine, Base
import app.models  # Ensures all models are registered with Base.metadata
from app.routers import (
    health_router,
    locations_router,
    overview_router,
    air_quality_router,
    water_quality_router,
    green_coverage_router,
    waste_management_router,
    noise_pollution_router,
    traffic_router,
    industrial_router,
    climate_router,
    chat_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created on application startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="EcoVision Environmental Intelligence API",
    description="Multi-dimensional environmental analytics and monitoring backend platform for India.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://eco-vision-wheat.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health_router)
app.include_router(locations_router)
app.include_router(overview_router)
app.include_router(air_quality_router)
app.include_router(water_quality_router)
app.include_router(green_coverage_router)
app.include_router(waste_management_router)
app.include_router(noise_pollution_router)
app.include_router(traffic_router)
app.include_router(industrial_router)
app.include_router(climate_router)
app.include_router(chat_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "platform": "EcoVision",
        "description": "Environmental Intelligence Platform Backend",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }
