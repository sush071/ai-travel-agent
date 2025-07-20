# backend/app/models/schema.py

from pydantic import BaseModel
from typing import List
 
class TripRequest(BaseModel):
    from_city: str
    destination_city: str
    start_date: str
    duration_days: str
    budget_inr: str
    interests: List[str]

class TripPlan(BaseModel):
    flights: str
    hotels: str
    itinerary: str
    visa: str

class TripResponse(BaseModel):
    plan: TripPlan
