from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import admin, auth, billing, crm, devices, usage


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create tables on startup so the app runs even before seeding.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Telecom CRM API",
    description="CRM for subscribers, telecom lines, devices, billing, and usage CDRs.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(auth.users_router)
app.include_router(crm.subscriber_router)
app.include_router(crm.line_router)
app.include_router(devices.router)
app.include_router(billing.router)
app.include_router(usage.router)
app.include_router(admin.router)


@app.get("/", tags=["root"])
def root():
    return {
        "message": "Telecom CRM API is running",
        "docs": "/docs",
        "token": "/token",
    }