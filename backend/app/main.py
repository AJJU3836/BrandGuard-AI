"""
BrandGuard AI — Main Application Entry Point

Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, brand_kits, dashboard, drafts, review, workspaces
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Create all tables (dev only — use Alembic migrations in production)
    Base.metadata.create_all(bind=engine)
    print("🛡️  BrandGuard AI Backend Started")
    yield
    print("🛡️  BrandGuard AI Backend Shutting Down")


app = FastAPI(
    title="BrandGuard AI",
    description="Intelligent Brand-Governance Platform — Pre-publication review powered by AI.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(brand_kits.router)
app.include_router(drafts.router)
app.include_router(review.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Root"])
def root():
    """Health check / welcome endpoint."""
    return {
        "message": "BrandGuard AI API",
        "version": "1.0.0",
        "docs": "/docs",
    }
