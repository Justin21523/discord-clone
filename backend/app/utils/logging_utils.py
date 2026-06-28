"""
Logging utilities for the Discord Clone application
"""

import logging
from datetime import datetime
import json
from typing import Any, Dict

# Configure the root logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a custom JSON formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'channel_id'):
            log_entry['channel_id'] = record.channel_id
        if hasattr(record, 'guild_id'):
            log_entry['guild_id'] = record.guild_id
        
        return json.dumps(log_entry)


def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Function to setup a logger with JSON formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # Optionally add file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger


def log_api_call(endpoint: str, method: str, user_id: int = None, success: bool = True):
    """
    Log an API call with relevant information
    """
    logger.info(
        f"API Call: {method} {endpoint}",
        extra={'user_id': user_id, 'success': success}
    )


def log_error(error_msg: str, user_id: int = None, error_type: str = None):
    """
    Log an error with relevant information
    """
    extra = {'error_type': error_type} if error_type else {}
    if user_id:
        extra['user_id'] = user_id
    
    logger.error(error_msg, extra=extra)


def log_security_event(event_type: str, user_id: int = None, details: Dict[str, Any] = None):
    """
    Log a security-related event
    """
    msg = f"Security Event: {event_type}"
    if details:
        msg += f" - Details: {details}"
    
    logger.warning(msg, extra={'user_id': user_id, 'security_event': True})