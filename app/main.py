from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Dict, Any
from hubspot.api import HubspotAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.crud import log_import
from app.models import ImportLog


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

items = []

class Lead(BaseModel):
    firstname:str | Any
    lastname:str | Any
    email:str | Any
    phone: str | Any
    company: str | Any

@app.post("/leads/batch/")
async def create_item(items: List[Lead] = Body(...)):

    response = HubspotAPI().batch_sync_contacts(items)
    log = log_import(
        db=next(get_db()),
        total_rows=len(items),
        created_count=response.get("created_count", 0),
        updated_count=response.get("updated_count", 0),
        error_count=response.get("error_count", 0),
        details=response.get("details", {}),
        errors= response.get("errors", {}),
    )

    print(f"Import log created with ID: {log.id}")

    return response

@app.post("/leads/sync/", response_model = Dict)
async def item_sync(item: Lead):
    response = HubspotAPI().create_contact(item)
    return response

@app.get("/logs/{log_id}")
async def get_log(log_id: int):
    db = next(get_db())
    log = db.query(ImportLog).filter(ImportLog.id == log_id).first()
    if not log:
        return {"error": "Log not found"}
    
    return {
        "id": log.id,
        "total_rows": log.total_rows,
        "created_count": log.created_count,
        "updated_count": log.updated_count,
        "error_count": log.error_count,
        "details": log.details,
        "errors": log.errors,
        "created_at": log.created_at.isoformat()
    }
