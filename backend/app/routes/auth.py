"""Authentication routes."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

from app.database import get_session
from app.models import User

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "teacher"

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True

def hash_password(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    """Register new user."""
    # Check if user exists
    query = select(User).where(User.email == request.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create token
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "role": user.role}
    }

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    """Login with email and password."""
    # Find user
    query = select(User).where(User.email == request.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "role": user.role}
    }

@router.post("/logout")
async def logout():
    """Logout endpoint (client should discard token)."""
    return {"message": "Logged out successfully"}

@router.post("/refresh", response_model=AuthResponse)
async def refresh(current_user: UserSchema = Depends(lambda token: token)):
    """Refresh token (placeholder)."""
    # In production, implement proper token refresh
    return {
        "access_token": "new_token_placeholder",
        "token_type": "bearer",
        "user": {"id": current_user.id, "email": current_user.email, "role": current_user.role}
    }
