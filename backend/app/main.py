from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.database import Base, engine
from app.routers import auth, alerts, incidents, threat_intel, analytics, users, audit

# Import models so SQLAlchemy metadata is registered before create_all.
from app.models import user, alert, incident, ioc, audit as audit_model  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "A Security Operations Center (SOC) platform for alert triage, incident "
        "response, threat intelligence correlation, and analytics. "
        "Built by Telnora Technologies."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(incidents.router)
app.include_router(threat_intel.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(audit.router)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/", tags=["meta"])
def root():
    return {
        "message": "Telnora SOC Platform API",
        "docs": "/docs",
        "company": "Telnora Technologies",
    }
