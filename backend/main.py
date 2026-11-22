from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy import text

from backend.config import settings
from backend.database.connection import engine


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered intelligent document organizer"
)


# ==========================================
# FRONTEND HOMEPAGE
# ==========================================

@app.get("/")
async def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ==========================================
# APPLICATION HEALTH CHECK
# ==========================================

@app.get("/api/health")
async def health_check():

    return {
        "status": "online",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# ==========================================
# DATABASE HEALTH CHECK
# ==========================================

@app.get("/api/health/database")
def database_health():

    try:

        with engine.connect() as connection:

            connection.execute(text("SELECT 1"))

        return {
            "database": "PostgreSQL",
            "status": "connected",
            "message": "AIDoc database connection successful"
        }

    except Exception as error:

        return {
            "database": "PostgreSQL",
            "status": "disconnected",
            "error": str(error)
        }


# ==========================================
# STATIC FILES
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)