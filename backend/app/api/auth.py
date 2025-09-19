"""
Authentication endpoints.

This module provides authentication endpoints for the API,
including login and token validation.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from ..core.auth import authenticate_user, create_access_token, get_current_user, User
from ..core.settings import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenResponse(BaseModel):
    """Token validation response model."""
    valid: bool
    user: Optional[dict] = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    This endpoint authenticates a user with username and password,
    returning a JWT token for subsequent API calls.
    """
    logger.info(f"Login attempt for user: {request.username}")
    
    user = authenticate_user(request.username, request.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user: {request.username}")
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.jwt_expire_minutes * 60,
        user={
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "scopes": user.scopes
        }
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    This endpoint returns information about the currently authenticated user.
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "scopes": current_user.scopes
    }


@router.post("/validate", response_model=TokenResponse)
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate a JWT token.
    
    This endpoint validates a JWT token and returns user information
    if the token is valid.
    """
    token = credentials.credentials
    user = get_current_user(token)
    
    if user:
        return TokenResponse(
            valid=True,
            user={
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "scopes": user.scopes
            }
        )
    else:
        return TokenResponse(valid=False)


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh a JWT token.
    
    This endpoint creates a new JWT token for the current user.
    """
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.username, "scopes": current_user.scopes},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Token refreshed for user: {current_user.username}")
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.jwt_expire_minutes * 60,
        user={
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "scopes": current_user.scopes
        }
    )
