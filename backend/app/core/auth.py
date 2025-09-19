"""
Authentication and authorization utilities.

This module provides JWT-based authentication for the Chrome extension
and API endpoints.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .settings import settings

# Security scheme
security = HTTPBearer()


class AuthManager:
    """Authentication manager."""
    
    def __init__(self):
        """Initialize auth manager."""
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.expire_minutes = settings.jwt_expire_minutes
    
    def create_token(self, data: Dict[str, Any]) -> str:
        """Create JWT token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Get current user from token."""
        token = credentials.credentials
        payload = self.verify_token(token)
        return payload


# Global auth manager
auth_manager = AuthManager()


def get_current_user(credentials: HTTPAuthorizationCredentials = security) -> Dict[str, Any]:
    """Dependency to get current user."""
    return auth_manager.get_current_user(credentials)


def create_extension_token() -> str:
    """Create token for Chrome extension."""
    return auth_manager.create_token({
        "type": "extension",
        "permissions": ["read", "write"]
    })