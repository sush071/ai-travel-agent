# backend/app/routes/travel.py

from fastapi import APIRouter
from app.models.schema import TripRequest, TripResponse, TripPlan
from app.utils.gemini import generate_trip_plan

router = APIRouter()

@router.post("/plan_trip/", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    plan_text = generate_trip_plan(request)
    
    # Split the response for frontend display
    sections = plan_text.split("###")
    plan = TripPlan(
        flights=sections[1].strip() if len(sections) > 1 else "No data",
        hotels=sections[2].strip() if len(sections) > 2 else "No data",
        itinerary=sections[3].strip() if len(sections) > 3 else "No data",
        visa=sections[4].strip() if len(sections) > 4 else "No data", 
    )

    return TripResponse(plan=plan)
