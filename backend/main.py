from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import router as auth_router
from backend.api import router as api_router

app = FastAPI()

origins = [
    "http://localhost:3000",  # Frontend (React/Vite/etc.)
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
