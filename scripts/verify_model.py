#!/usr/bin/env python3
"""
Verify RVC model for Voice Transformer
"""

import os
import sys
import argparse
import torch
import json
from pathlib import Path

def verify_model(model_path, verbose=False):
    """
    Verify RVC model file
    
    Args:
        model_path (str): Path to model file
        verbose (bool, optional): Print detailed information. Defaults to False.
    
    Returns:
        bool: True if model is valid, False otherwise
    """
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(model_path)
    print(f"Model file size: {file_size / (1024 * 1024):.2f} MB")
    
    # For a real RVC model, we would try to load it here and verify its structure
    # This is a simplified placeholder implementation that just checks if the file exists
    
    print(f"NOTE: This is a simplified verification for demonstration purposes.")
    print(f"In a real implementation, this would load and verify the actual model structure.")
    
    # Check for model config file
    model_dir = os.path.dirname(model_path)
    config_path = os.path.join(model_dir, "model_config.json")
    
    if os.path.exists(config_path):
        print(f"Found model configuration at {config_path}")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("\nModel Information:")
            print(f"Name: {config.get('model_name', 'Unknown')}")
            print(f"Version: {config.get('version', 'Unknown')}")
            print(f"Language: {config.get('language', 'Unknown')}")
            print(f"Voice Type: {config.get('voice_type', 'Unknown')}")
            print(f"Sample Rate: {config.get('sample_rate', 'Unknown')} Hz")
            
            if verbose:
                print("\nFull Configuration:")
                for key, value in config.items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"Error reading model configuration: {e}")
    else:
        print(f"No model configuration found at {config_path}")
    
    # Try to simulate loading the model with PyTorch
    print("\nAttempting to simulate model loading...")
    try:
        # This is just a simulation - in a real implementation, 
        # we would load the actual RVC model here
        if file_size > 0:
            print("Model file appears to be valid")
            return True
        else:
            print("Model file is empty")
            return False
    except Exception as e:
        print(f"Error during model verification: {e}")
        return False

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Verify RVC model for Voice Transformer')
    parser.add_argument('--model-path', type=str, default="../models/vietnamese_female.pt", 
                        help='Path to model file')
    parser.add_argument('--verbose', action='store_true', 
                        help='Print detailed information')
    
    args = parser.parse_args()
    
    # Normalize path
    model_path = os.path.normpath(os.path.expanduser(args.model_path))
    
    # Verify model
    success = verify_model(model_path, args.verbose)
    
    if success:
        print("\nModel verification successful")
        sys.exit(0)
    else:
        print("\nModel verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 