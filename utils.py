import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Base directory for logs
LOG_DIR = Path(__file__).resolve().parent
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Log file names with date
def get_log_files():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return {
        'main': LOG_DIR / f"main_log_{date_str}.log",
        'error': LOG_DIR / f"main_errors_{date_str}.log"
    }

# Configure logging
def setup_logging(name="zimchu-scraper"):
    """Set up logging for the application with both file and console handlers"""
    logger = logging.getLogger(name)
    # Only set up handlers if they don't exist
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatters
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        
        # Get log files
        log_files = get_log_files()
        
        # Setup file handler for all logs
        file_handler = logging.FileHandler(log_files['main'])
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
        # Setup file handler for errors only
        error_file_handler = logging.FileHandler(log_files['error'])
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)
        
        # Setup console handler (visible in terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def print_demarkers(title: str):
    """Print section dividers - now also logs the information"""
    message = f"==========================={title}==========================="
    print(f"\n{message}\n")
    # Get the logger for the caller module
    logger = logging.getLogger('zimchu-scraper')
    logger.info(message)
