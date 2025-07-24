from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import SessionLocal
from backend.infrastructure.models import User
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    redirect: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt(user_id, role):
    return jwt.encode({"sub": str(user_id), "role": role}, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate(credentials: LoginRequest, db: AsyncSession):
    result = await db.execute(
        User.__table__.select().where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()
    if user and verify_password(credentials.password, user.password_hash):
        return user
    return None

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(SessionLocal)):
    user = await authenticate(credentials, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {
        "access_token": create_jwt(user.id, user.role),
        "redirect": f"https://{user.role}.djamms.app/dashboard"
    }
