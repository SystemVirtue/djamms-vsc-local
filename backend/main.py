from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.auth import router as auth_router
from backend.api import router as api_router
from backend.media_api import router as media_router

app = FastAPI()

# Mount static files for audio uploads
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

origins = [
    "http://localhost:3000",  # Frontend (React/Vite/etc.)
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",  # Backend (API docs, etc.)
    # Add your production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router)
app.include_router(media_router)
