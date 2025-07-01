# medassistant/backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db_session import engine, Base
from app.scheduler import start_scheduler

from app.auth_security import auth_router
from app.routes.items import router as items_router
from app.routes.sensors import router as sensors_router
from app.routes.sensors_status import router as sensors_status_router
from app.routes.alerts import router as alerts_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="MedAssistant API",
        version="1.0.0",
        description="Backend for NFC/sensor traceability and environmental monitoring"
    )

    # Allow CORS for frontend (adjust origins in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create all tables (for MVP; migrate to Alembic later if needed)
    Base.metadata.create_all(bind=engine)

    # Authentication routes (login, token)
    app.include_router(auth_router, prefix="/auth", tags=["auth"])

    # Domain routes
    app.include_router(items_router, prefix="/items", tags=["items"])
    app.include_router(sensors_router, prefix="/sensors", tags=["sensors"])
    app.include_router(sensors_status_router, prefix="/sensors", tags=["sensors-status"])
    app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])

    # Startup event to begin background scheduler
    @app.on_event("startup")
    def on_startup():
        start_scheduler()

    return app

app = create_app()





