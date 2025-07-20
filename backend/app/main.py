from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Import the necessary components from your other backend files
from .models.schema import TripRequest
from .utils.gemini import generate_trip_plan

# A simple list of cities for suggestions.
# In a real application, this could come from a database or a more extensive API.
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Surat", "Pune", "Jaipur",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad",
    "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
    "Amritsar", "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur",
    "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh", "Solapur", "Hubli-Dharwad", "Bareilly", "Moradabad",
    "Mysore", "Gurgaon", "Aligarh", "Jalandhar", "Tiruchirappalli", "Bhubaneswar", "Salem", "Warangal", "Guntur",
    "Bhiwandi", "Saharanpur", "Gorakhpur", "Bikaner", "Amravati", "Noida", "Jamshedpur", "Bhilai", "Cuttack",
    "Firozabad", "Kochi", "Nellore", "Bhavnagar", "Dehradun", "Durgapur", "Asansol", "Rourkela", "Nanded",
    "Kolhapur", "Ajmer", "Gulbarga", "Jamnagar", "Ujjain", "Loni", "Siliguri", "Jhansi", "Ulhasnagar", "Jammu",
    "Sangli-Miraj & Kupwad", "Mangalore", "Erode", "Belgaum", "Ambattur", "Tirunelveli", "Malegaon", "Gaya",
    "Jalgaon", "Udaipur", "Maheshtala",
    "New York", "London", "Paris", "Tokyo", "Dubai", "Singapore", "Rome", "Barcelona", "Sydney", "Amsterdam",
    "Bangkok", "Hong Kong", "Istanbul", "Vienna", "Prague", "Los Angeles", "San Francisco", "Chicago", "Toronto",
    "Berlin", "Madrid", "Moscow", "Beijing", "Shanghai", "Seoul", "Kuala Lumpur", "Dublin", "Lisbon", "Athens"
]

def parse_plan(plan_text: str) -> dict:
    """Parses the raw text from the AI into a structured dictionary."""
    sections = {}
    current_section = None
    
    # Maps the section titles from the AI prompt to the keys the frontend expects
    key_mapping = {
        "Transportation": "transportation",
        "Hotels": "hotels",
        "Itinerary": "itinerary",
        "Docs": "visa"
    }

    for line in plan_text.strip().split('\n'):
        if line.startswith("### "):
            section_title = line[4:].strip()
            current_section = key_mapping.get(section_title)
            if current_section:
                sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())

    # Join the lines for each section back into a single string
    for key, value_lines in sections.items():
        sections[key] = "\n".join(value_lines)
        
    return sections

app = FastAPI()

# CORS is still useful for local development
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cities/")
def get_cities(q: str = ""):
    """Provides a list of cities for autocomplete suggestions."""
    if not q:
        return []
    
    # Filter cities based on the query (case-insensitive) and return top 10 matches
    suggestions = [city for city in CITIES if q.lower() in city.lower()]
    return suggestions[:10]

# Define the API endpoint directly in this file
@app.post("/plan_trip/")
def plan_trip(request: TripRequest):
    raw_plan_text = generate_trip_plan(request)
    parsed_plan = parse_plan(raw_plan_text)
    return {"plan": parsed_plan}

# --- Serve React App ---
# This section serves the built React app's static files.
# It assumes the 'build' directory is at the root of your project.
build_dir = Path(__file__).resolve().parent.parent.parent / "build"

if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="static")
else:
    print(f"Build directory not found at {build_dir}. Frontend will not be served in production.")