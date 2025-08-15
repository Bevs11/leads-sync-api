from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from hubspot.api import HubspotAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    firstname:str
    lastname:str
    email:str
    phone: str 
    company: str

@app.post("/leads/batch/")
async def create_item(items: List[Lead]):
    response = HubspotAPI().batch_sync_contacts(items)
    return response

@app.post("/leads/sync/", response_model = Dict)
async def create_item(item: Lead):
    response = HubspotAPI().create_contact(item)
    return response


