"""Structured logging configuration for Refund Service"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record.__dict__
        extra_fields = {k: v for k, v in record.__dict__.items() 
                       if k not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 
                                  'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
                                  'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process']}
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry)

def log_api_request(logger: logging.Logger, method: str, path: str, status_code: int, 
                   user_id: str = "", duration_ms: float = 0.0, **extra) -> None:
    """Log API request details"""
    log_data = {
        "type": "api_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "user_id": user_id,
        "duration_ms": duration_ms,
        **extra
    }
    
    # Remove None/empty values
    log_data = {k: v for k, v in log_data.items() if v not in ["", 0.0] and v is not None}
    
    extra_params = {"extra": log_data}
    
    logger.info(f"API {method} {path} - {status_code}", extra=extra_params)

def log_error(logger: logging.Logger, error_type: str, error_message: str, 
             user_id: str = "", **extra) -> None:
    """Log error with structured data"""
    log_data = {
        "type": "error",
        "error_type": error_type,
        "user_id": user_id,
        **extra
    }
    
    # Remove None/empty values
    log_data = {k: v for k, v in log_data.items() if v != "" and v is not None}
    
    extra_params = {"extra": log_data}
    
    logger.error(error_message, extra=extra_params)

def log_business_event(logger: logging.Logger, event_type: str, message: str,
                     case_id: str = "", user_id: str = "", **extra) -> None:
    """Log business events"""
    log_data = {
        "type": "business_event",
        "event_type": event_type,
        "case_id": case_id,
        "user_id": user_id,
        **extra
    }
    
    # Remove None/empty values
    log_data = {k: v for k, v in log_data.items() if v != "" and v is not None}
    
    extra_params = {"extra": log_data}
    
    logger.info(message, extra=extra_params)