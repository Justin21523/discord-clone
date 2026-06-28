"""
Custom exceptions for the Discord Clone application
"""

from fastapi import HTTPException, status


class DiscordCloneException(HTTPException):
    """Base exception class for Discord Clone application"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationException(DiscordCloneException):
    """Raised when authentication fails"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(DiscordCloneException):
    """Raised when authorization fails"""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ResourceNotFoundException(DiscordCloneException):
    """Raised when a requested resource is not found"""
    def __init__(self, resource_type: str, resource_id: int = None):
        if resource_id:
            detail = f"{resource_type} with ID {resource_id} not found"
        else:
            detail = f"{resource_type} not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class RateLimitException(DiscordCloneException):
    """Raised when rate limit is exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class DuplicateResourceException(DiscordCloneException):
    """Raised when trying to create a duplicate resource"""
    def __init__(self, resource_type: str, field: str, value: str):
        detail = f"{resource_type} with {field} '{value}' already exists"
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)