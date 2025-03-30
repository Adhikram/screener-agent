"""Logger utility for the AI Resume Reviewer"""
import logging
import sys

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    logger = logging.getLogger("resume_reviewer")
    logger.setLevel(log_level)
    
    # Create a handler for console output
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Format logs
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger 