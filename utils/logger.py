"""
Logging configuration for the application.
"""
import logging
import sys
from datetime import datetime

def setup_logger(name: str = "quiz_generator") -> logging.Logger:
    """
    Set up a detailed logger for the application.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Console handler with detailed formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Detailed format with timestamp, level, module, and message
    formatter = logging.Formatter(
        '\n%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d\n'
        '→ %(message)s\n' + '-' * 80,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logger()

def log_step(step: str, details: str = ""):
    """Log a processing step with visual separation."""
    logger.info(f"📌 STEP: {step}\n   {details}")

def log_success(message: str):
    """Log a success message."""
    logger.info(f"✅ SUCCESS: {message}")

def log_error(message: str, error: Exception = None):
    """Log an error message."""
    if error:
        logger.error(f"❌ ERROR: {message}\n   Exception: {str(error)}")
    else:
        logger.error(f"❌ ERROR: {message}")

def log_debug(message: str):
    """Log a debug message."""
    logger.debug(f"🔍 DEBUG: {message}")

