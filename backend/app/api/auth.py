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

from ..core.auth import AuthManager, get_current_user, create_extension_token
from ..core.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer()

# Initialize auth manager
auth_manager = AuthManager()

# Request/Response models
class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str

class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenResponse(BaseModel):
    """Token validation response model."""
    valid: bool
    user: Optional[dict] = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    This endpoint authenticates a user with email and password,
    returning a JWT token for subsequent API calls.
    """
    logger.info(f"Login attempt for user: {request.email}")
    
    # For demo purposes, accept any email/password
    if request.email and request.password:
        access_token = auth_manager.create_token({
            "sub": request.email,
            "email": request.email,
            "name": request.email.split('@')[0],
            "scopes": ["read", "write"]
        })
        
        logger.info(f"Successful login for user: {request.email}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60
        )
    else:
        logger.warning(f"Failed login attempt for user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email and password are required",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information.
    
    This endpoint returns information about the currently authenticated user.
    """
    return current_user


@router.post("/validate", response_model=TokenResponse)
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate JWT token.
    
    This endpoint validates a JWT token and returns user information.
    """
    try:
        user = auth_manager.verify_token(credentials.credentials)
        return TokenResponse(valid=True, user=user)
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        return TokenResponse(valid=False)


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh JWT token.
    
    This endpoint refreshes the current user's JWT token.
    """
    access_token = auth_manager.create_token({
        "sub": current_user.get("sub", "unknown"),
        "scopes": current_user.get("scopes", ["read"])
    })
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60
    )


@router.post("/extension-token", response_model=LoginResponse)
async def create_extension_token_endpoint():
    """
    Create a token for Chrome extension.
    
    This endpoint creates a special token for the Chrome extension
    that doesn't require user authentication.
    """
    token = create_extension_token()
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60
    )