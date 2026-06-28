"""
Input validation utilities for the Discord Clone application
"""

import re
from typing import Optional
from pydantic import validator
from pydantic.types import constr


def validate_username(username: str) -> bool:
    """
    Validate username according to Discord-like rules:
    - 2-32 characters
    - Letters, numbers, underscores, hyphens only
    - Cannot start or end with underscore or hyphen
    """
    if len(username) < 2 or len(username) > 32:
        return False
    
    # Check allowed characters and pattern
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^([a-zA-Z0-9])$'
    return bool(re.match(pattern, username))


def validate_email(email: str) -> bool:
    """
    Basic email validation
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_channel_name(name: str) -> bool:
    """
    Validate channel name:
    - 1-100 characters
    - Letters, numbers, spaces, hyphens, underscores only
    - Cannot start or end with space
    """
    if len(name) < 1 or len(name) > 100:
        return False
    
    if name.startswith(' ') or name.endswith(' '):
        return False
    
    # Check allowed characters
    pattern = r'^[a-zA-Z0-9-_ ]+$'
    return bool(re.match(pattern, name))


def validate_guild_name(name: str) -> bool:
    """
    Validate guild/server name:
    - 1-100 characters
    - Any printable character except control characters
    """
    if len(name) < 1 or len(name) > 100:
        return False
    
    # Check for control characters (ASCII 0-31 and 127)
    return not any(ord(c) < 32 or ord(c) == 127 for c in name)


def validate_message_content(content: str) -> bool:
    """
    Validate message content:
    - 1-2000 characters
    - No control characters except tab, newline, carriage return
    """
    if len(content) < 1 or len(content) > 2000:
        return False
    
    # Check for invalid control characters (excluding tab, newline, carriage return)
    for c in content:
        if ord(c) < 32 and c not in '\t\n\r':
            return False
        if ord(c) == 127:  # DEL character
            return False
    
    return True


def sanitize_input(text: str) -> str:
    """
    Basic input sanitization to prevent simple injection attacks
    """
    # Remove null bytes
    sanitized = text.replace('\x00', '')
    
    # Remove control characters (except tab, newline, carriage return)
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\t\n\r')
    
    return sanitized