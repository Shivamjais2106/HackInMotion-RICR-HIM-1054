"""Logging Configuration for KisanSathi Backend"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Log file paths
LOG_FILE = os.path.join(LOG_DIR, f'kisansathi_{datetime.now().strftime("%Y%m%d")}.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, f'errors_{datetime.now().strftime("%Y%m%d")}.log')
API_LOG_FILE = os.path.join(LOG_DIR, f'api_{datetime.now().strftime("%Y%m%d")}.log')

def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Main logger
    main_logger = logging.getLogger('kisansathi')
    main_logger.setLevel(logging.DEBUG)
    
    # API logger
    api_logger = logging.getLogger('kisansathi.api')
    api_logger.setLevel(logging.INFO)
    
    # Error logger
    error_logger = logging.getLogger('kisansathi.error')
    error_logger.setLevel(logging.ERROR)
    
    # Formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    api_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Main file handler (rotating)
    main_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(detailed_formatter)
    main_logger.addHandler(main_handler)
    
    # API file handler
    api_handler = logging.handlers.RotatingFileHandler(
        API_LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=5
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(api_formatter)
    api_logger.addHandler(api_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    error_logger.addHandler(error_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    main_logger.addHandler(console_handler)
    
    return main_logger, api_logger, error_logger

def get_logger(name):
    """Get logger instance"""
    return logging.getLogger(f'kisansathi.{name}')

def log_api_request(method, endpoint, status_code, response_time):
    """Log API request"""
    api_logger = logging.getLogger('kisansathi.api')
    api_logger.info(f'{method} {endpoint} - Status: {status_code} - Time: {response_time:.2f}ms')

def log_error(error_type, message, details=None):
    """Log error"""
    error_logger = logging.getLogger('kisansathi.error')
    if details:
        error_logger.error(f'{error_type}: {message} - Details: {details}')
    else:
        error_logger.error(f'{error_type}: {message}')
