from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Import the necessary components from your other backend files
from .models.schema import TripRequest
from .utils.gemini import generate_trip_plan

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