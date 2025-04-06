#!/usr/bin/env python3
"""
Download RVC model for Voice Transformer
"""

import os
import sys
import argparse
import requests
import shutil
import zipfile
import hashlib
from tqdm import tqdm
import json

# Default model URL and file info
# Note: This is a placeholder URL. In a real implementation, this would point to an actual model file.
DEFAULT_MODEL_URL = "https://example.com/models/vietnamese_female_voice_model.zip"
DEFAULT_MODEL_SIZE = 300 * 1024 * 1024  # 300 MB
DEFAULT_MODEL_HASH = "0123456789abcdef0123456789abcdef"  # Example MD5 hash

def download_file(url, destination, expected_size=None):
    """
    Download a file with progress display
    
    Args:
        url (str): URL to download
        destination (str): Destination file path
        expected_size (int, optional): Expected file size in bytes. Defaults to None.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size if not provided
        file_size = expected_size or int(response.headers.get('content-length', 0))
        
        # Show progress bar
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc="Downloading")
        
        # Download file
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        progress_bar.close()
        
        # Check if file size matches expected size
        actual_size = os.path.getsize(destination)
        if expected_size and actual_size != expected_size:
            print(f"WARNING: Downloaded file size ({actual_size} bytes) does not match expected size ({expected_size} bytes)")
        
        return True
    
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def verify_file(file_path, expected_hash=None):
    """
    Verify file integrity using MD5 hash
    
    Args:
        file_path (str): Path to file
        expected_hash (str, optional): Expected MD5 hash. Defaults to None.
    
    Returns:
        bool: True if hash matches or no hash check requested, False otherwise
    """
    if not expected_hash:
        return True
    
    print("Verifying file integrity...")
    
    try:
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        
        file_hash = md5_hash.hexdigest()
        
        if file_hash != expected_hash:
            print(f"WARNING: File hash ({file_hash}) does not match expected hash ({expected_hash})")
            return False
        
        print("File integrity verified successfully")
        return True
    
    except Exception as e:
        print(f"Error verifying file: {e}")
        return False

def extract_zip(zip_path, extract_dir):
    """
    Extract ZIP file
    
    Args:
        zip_path (str): Path to ZIP file
        extract_dir (str): Directory to extract to
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Extracting {zip_path} to {extract_dir}...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print("Extraction completed successfully")
        return True
    
    except Exception as e:
        print(f"Error extracting file: {e}")
        return False

def simulate_download(destination_dir, model_name="vietnamese_female.pt"):
    """
    Simulate model download for demonstration purposes
    
    Args:
        destination_dir (str): Destination directory
        model_name (str, optional): Model file name. Defaults to "vietnamese_female.pt".
    
    Returns:
        bool: Always True (success)
    """
    print("\nNOTE: This is a simulation of model download for demonstration purposes.")
    print("In a real implementation, this would download the actual model file.\n")
    
    # Ensure directory exists
    os.makedirs(destination_dir, exist_ok=True)
    
    # Path to model file
    model_path = os.path.join(destination_dir, model_name)
    
    # Create a dummy model file
    print(f"Creating dummy model file at {model_path}...")
    with open(model_path, 'wb') as f:
        # Write some random data to simulate a model file
        f.write(os.urandom(1024))
    
    # Create a model config file with metadata
    config_path = os.path.join(destination_dir, "model_config.json")
    config = {
        "model_name": "RVC Vietnamese Female Voice Model",
        "version": "1.0.0",
        "language": "Vietnamese",
        "voice_type": "female",
        "sample_rate": 16000,
        "created_date": "2023-06-15",
        "description": "A voice conversion model trained on Vietnamese female voice samples"
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Dummy model files created successfully")
    return True

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Download RVC model for Voice Transformer')
    parser.add_argument('--url', type=str, default=DEFAULT_MODEL_URL, 
                        help='URL to download model from')
    parser.add_argument('--output-dir', type=str, default="../models", 
                        help='Directory to save model to')
    parser.add_argument('--model-name', type=str, default="vietnamese_female.pt", 
                        help='Name of the model file')
    parser.add_argument('--verify', action='store_true', 
                        help='Verify file integrity after download')
    parser.add_argument('--simulate', action='store_true', 
                        help='Simulate download for demonstration purposes')
    
    args = parser.parse_args()
    
    # Normalize path
    output_dir = os.path.normpath(os.path.expanduser(args.output_dir))
    model_path = os.path.join(output_dir, args.model_name)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Model will be saved to: {model_path}")
    
    # Check if model already exists
    if os.path.exists(model_path):
        overwrite = input("Model file already exists. Overwrite? (y/n): ").lower() == 'y'
        if not overwrite:
            print("Download cancelled")
            return
    
    # Simulate download for demonstration
    if args.simulate:
        success = simulate_download(output_dir, args.model_name)
    else:
        # Real download process
        temp_file = f"{model_path}.download"
        
        # Download model
        print(f"Downloading model from {args.url}...")
        success = download_file(args.url, temp_file, DEFAULT_MODEL_SIZE)
        
        if success and args.verify:
            # Verify downloaded file
            success = verify_file(temp_file, DEFAULT_MODEL_HASH)
        
        if success:
            # If file is a ZIP archive, extract it
            if args.url.endswith('.zip'):
                extract_success = extract_zip(temp_file, output_dir)
                if extract_success:
                    # Clean up ZIP file
                    os.remove(temp_file)
            else:
                # Move downloaded file to final location
                shutil.move(temp_file, model_path)
        else:
            # Clean up partial download
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    if success:
        print("\nModel download completed successfully!")
        print(f"Model saved to: {model_path}")
    else:
        print("\nError downloading model")
        print("Please try again or download the model manually.")
        print(f"Manual download URL: {args.url}")
        print(f"Save the file to: {model_path}")

if __name__ == "__main__":
    main() 