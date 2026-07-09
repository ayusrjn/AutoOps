from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhook, incidents
from app.database import engine
from app.models.incident import Base

# Create all database tables (SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoOps",
    description="AI-powered, self-hosted incident commander API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # To be updated in Prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(incidents.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
