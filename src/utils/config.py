"""
Configuration utilities for Voice Transformer
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config(config_path):
    """
    Load configuration from JSON file
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Configuration file {config_path} not found, using default configuration")
        return create_default_config()
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing configuration file: {e}")
        logger.warning("Using default configuration")
        return create_default_config()

def create_default_config():
    """
    Create default configuration
    
    Returns:
        dict: Default configuration dictionary
    """
    return {
        "audio": {
            "input_device": None,
            "output_device": None,
            "sample_rate": 16000,
            "buffer_size": 512,
            "channels": 1,
            "format": "int16"
        },
        "transformation": {
            "model_path": "models/vietnamese_female.pt",
            "pitch_shift": 5.0,
            "formant_shift": 1.2,
            "intensity": 0.8,
            "preserve_tones": True
        },
        "performance": {
            "threads": 2,
            "max_latency_ms": 100,
            "auto_adjust_buffer": True,
            "enable_gpu": False
        },
        "logging": {
            "level": "INFO",
            "file": "logs/voice_transformer.log",
            "max_file_size_mb": 10,
            "backup_count": 3
        },
        "ui": {
            "refresh_rate_ms": 250,
            "show_metrics": True,
            "color_output": True
        }
    }

def save_config(config, config_path):
    """
    Save configuration to JSON file
    
    Args:
        config (dict): Configuration dictionary
        config_path (str): Path to save configuration file
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False 