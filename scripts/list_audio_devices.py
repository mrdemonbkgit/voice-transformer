#!/usr/bin/env python3
"""
List available audio devices
"""

import pyaudio
import sys

def list_audio_devices():
    """
    List available audio input and output devices
    """
    # Initialize PyAudio
    pa = pyaudio.PyAudio()
    
    try:
        print("\nAvailable Audio Devices:")
        print("========================\n")
        
        # Get device count
        device_count = pa.get_device_count()
        print(f"Found {device_count} audio devices\n")
        
        # List input devices
        print("Input Devices:")
        print("-------------")
        for i in range(device_count):
            device_info = pa.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"[{i}] {device_info['name']}")
                print(f"    Channels: {device_info['maxInputChannels']}")
                print(f"    Sample Rate: {int(device_info['defaultSampleRate'])} Hz")
                print()
        
        # List output devices
        print("Output Devices:")
        print("--------------")
        for i in range(device_count):
            device_info = pa.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                print(f"[{i}] {device_info['name']}")
                print(f"    Channels: {device_info['maxOutputChannels']}")
                print(f"    Sample Rate: {int(device_info['defaultSampleRate'])} Hz")
                print()
        
        # Show default devices
        default_input = pa.get_default_input_device_info()
        default_output = pa.get_default_output_device_info()
        
        print("Default Devices:")
        print("---------------")
        print(f"Default Input: [{default_input['index']}] {default_input['name']}")
        print(f"Default Output: [{default_output['index']}] {default_output['name']}")
        
    except Exception as e:
        print(f"Error listing audio devices: {e}")
    finally:
        # Clean up
        pa.terminate()

if __name__ == "__main__":
    list_audio_devices() 