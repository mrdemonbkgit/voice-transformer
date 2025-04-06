#!/usr/bin/env python3
"""
Test audio input and output
"""

import pyaudio
import numpy as np
import time
import argparse
import sys

def test_audio(input_device=None, output_device=None, duration=5, sample_rate=16000):
    """
    Test audio input and output by recording and playing back audio
    
    Args:
        input_device (int, optional): Input device index. Defaults to None (system default).
        output_device (int, optional): Output device index. Defaults to None (system default).
        duration (int, optional): Test duration in seconds. Defaults to 5.
        sample_rate (int, optional): Sample rate in Hz. Defaults to 16000.
    """
    # Initialize PyAudio
    pa = pyaudio.PyAudio()
    
    try:
        # Get device info
        if input_device is not None:
            try:
                input_info = pa.get_device_info_by_index(input_device)
                print(f"Using input device: [{input_device}] {input_info['name']}")
            except Exception:
                print(f"Invalid input device index: {input_device}")
                print("Using default input device")
                input_device = None
        
        if output_device is not None:
            try:
                output_info = pa.get_device_info_by_index(output_device)
                print(f"Using output device: [{output_device}] {output_info['name']}")
            except Exception:
                print(f"Invalid output device index: {output_device}")
                print("Using default output device")
                output_device = None
        
        # Parameters
        chunk_size = 1024
        channels = 1
        format = pyaudio.paInt16
        
        # Buffer to store audio data
        audio_data = []
        
        # Define callback function for input stream
        def callback(in_data, frame_count, time_info, status):
            audio_data.append(in_data)
            return (in_data, pyaudio.paContinue)
        
        # Open input stream
        print(f"\nRecording for {duration} seconds...")
        input_stream = pa.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=input_device,
            frames_per_buffer=chunk_size,
            stream_callback=callback
        )
        
        # Start recording
        input_stream.start_stream()
        
        # Wait for recording to complete
        time.sleep(duration)
        
        # Stop recording
        input_stream.stop_stream()
        input_stream.close()
        
        print("Recording finished")
        
        # Combine all audio chunks
        recorded_audio = b''.join(audio_data)
        
        # Convert to numpy array for analysis
        audio_array = np.frombuffer(recorded_audio, dtype=np.int16)
        
        # Analyze audio
        max_amp = np.max(np.abs(audio_array))
        max_amp_db = 20 * np.log10(max_amp / 32767) if max_amp > 0 else -100
        
        print("\nAudio Analysis:")
        print(f"Max amplitude: {max_amp} ({max_amp_db:.1f} dB)")
        
        if max_amp < 100:
            print("WARNING: Very low audio levels detected. Check microphone.")
        elif max_amp > 32000:
            print("WARNING: Audio clipping detected. Microphone volume may be too high.")
        else:
            print("Audio levels look good!")
        
        # Playback the recorded audio
        print("\nPlaying back recorded audio...")
        
        # Open output stream
        output_stream = pa.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            output=True,
            output_device_index=output_device,
            frames_per_buffer=chunk_size
        )
        
        # Start playback
        output_stream.start_stream()
        
        # Write audio data in chunks
        for i in range(0, len(recorded_audio), chunk_size * 2):
            chunk = recorded_audio[i:i + chunk_size * 2]
            output_stream.write(chunk)
        
        # Stop playback
        output_stream.stop_stream()
        output_stream.close()
        
        print("Playback finished")
        print("\nAudio test completed successfully!")
        
    except Exception as e:
        print(f"\nError testing audio: {e}")
        return False
    finally:
        # Clean up
        pa.terminate()
    
    return True

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Test audio input and output')
    parser.add_argument('--input-device', type=int, help='Input device index')
    parser.add_argument('--output-device', type=int, help='Output device index')
    parser.add_argument('--duration', type=int, default=5, help='Test duration in seconds')
    parser.add_argument('--sample-rate', type=int, default=16000, help='Sample rate in Hz')
    parser.add_argument('--list-devices', action='store_true', help='List available audio devices')
    
    args = parser.parse_args()
    
    # List devices if requested
    if args.list_devices:
        from list_audio_devices import list_audio_devices
        list_audio_devices()
        return
    
    # Run audio test
    test_audio(
        input_device=args.input_device, 
        output_device=args.output_device,
        duration=args.duration,
        sample_rate=args.sample_rate
    )

if __name__ == "__main__":
    main() 