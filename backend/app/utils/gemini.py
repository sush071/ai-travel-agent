# backend/app/utils/gemini.py

import google.generativeai as genai
from app.models.schema import TripRequest
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
 
def generate_trip_plan(request: TripRequest) -> str:
    prompt = f"""
    You are a smart AI travel agent.
    
    Plan a detailed trip for:
    From: {request.from_city}
    To: {request.destination_city}
    Start Date: {request.start_date}
    Duration: {request.duration_days} days
    Budget: ₹{request.budget_inr}
    Interests: {", ".join(request.interests)}

    Return the result in this format:
    ### Transportation
    Provide a detailed transportation plan. Include the easiest and most cost-effective options for travel between the cities. Also, include details on local public transport like buses and trains, and options for private car or bike rentals at the destination. Use sub-headings for clarity.
    ### Hotels
    [Hotel details]
    ### Itinerary
    [Itinerary day by day, including activities, meals, and transport]
    **Day 1:** [Activities]
    **Day 2:** [Activities]
    ### Docs
    [Visa and other required documentation information]
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text 
