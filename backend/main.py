"""
RoadPulse Backend - AI-Powered Real-Time Traffic Notification App

This module initializes the FastAPI application with all necessary middleware,
routes, and startup/shutdown events.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import users, routes as route_routes, notifications
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events (startup and shutdown).
    """
    # Startup
    print("Starting up RoadPulse API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # Start background scheduler for traffic polling
    start_scheduler()
    print("Traffic polling scheduler started.")
    
    yield
    
    # Shutdown
    print("Shutting down RoadPulse API...")
    stop_scheduler()
    print("Scheduler stopped.")


app = FastAPI(
    title="RoadPulse API",
    description="AI-powered real-time traffic notification backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(route_routes.router, prefix="/api/v1/routes", tags=["Routes"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RoadPulse API"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
