from fastapi import Request, HTTPException, status, Depends
from jose import JWTError, jwt
from typing import Optional
from backend.infrastructure.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import SessionLocal
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(lambda: None)) -> User:
    """
    Dependency to get the current authenticated user.
    For now, this is a placeholder that allows access without authentication.
    """
    # For development purposes, return a mock user
    # In production, this should properly validate the JWT token
    mock_user = User(
        id=1,
        username="dev_user",
        email="dev@example.com",
        role="admin",
        is_active=True
    )
    return mock_user

async def security_middleware(request: Request, call_next):
    token = request.headers.get("Authorization", None)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token authentication required"
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    async with SessionLocal() as db:
        user = await db.execute(
            User.__table__.select().where(User.id == user_id)
        )
        db_user = user.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        
        if db_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
        
    return await call_next(request, user=db_user, role=role)