"""
Logging utilities for Voice Transformer
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging(config):
    """
    Set up logging configuration
    
    Args:
        config (dict): Logging configuration dictionary
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config['file'])
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config['level'].upper()))
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        config['file'],
        maxBytes=config['max_file_size_mb'] * 1024 * 1024,
        backupCount=config['backup_count']
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Create our application logger
    app_logger = logging.getLogger('voice_transformer')
    
    return app_logger 