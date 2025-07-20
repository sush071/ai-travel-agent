from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import trip
from pathlib import Path
import os

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

# This includes your API route (e.g., /plan_trip/)
app.include_router(trip.router)

# --- Serve React App ---
# This section serves the built React app's static files.
# It assumes the 'build' directory is at the root of your project.
build_dir = Path(__file__).resolve().parent.parent.parent / "build"

if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="static")
else:
    print(f"Build directory not found at {build_dir}. Frontend will not be served in production.")