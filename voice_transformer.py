#!/usr/bin/env python3
"""
Voice Transformer - Real-time male to female voice transformation

A Windows CLI application for transforming voice from male to female in real time,
optimized for Vietnamese speech.
"""

import os
import sys
import argparse
import json
import time
import signal
from pathlib import Path

from src.audio.input import AudioInput
from src.audio.output import AudioOutput
from src.audio.processing import AudioProcessor
from src.transformation.pipeline import TransformationPipeline
from src.cli.commands import CommandHandler
from src.cli.display import Display
from src.utils.config import load_config
from src.utils.logging import setup_logging

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle interrupt signals for graceful shutdown"""
    global running
    print("\nShutting down Voice Transformer...")
    running = False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Voice Transformer - Real-time voice transformation')
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to configuration file')
    parser.add_argument('--input-device', type=int, 
                        help='Input device index')
    parser.add_argument('--output-device', type=int,
                        help='Output device index')
    parser.add_argument('--buffer-size', type=int,
                        help='Audio buffer size in samples')
    parser.add_argument('--sample-rate', type=int,
                        help='Audio sample rate in Hz')
    parser.add_argument('--pitch-shift', type=float,
                        help='Pitch shift amount in semitones')
    parser.add_argument('--formant-shift', type=float,
                        help='Formant shift factor')
    parser.add_argument('--save-config', type=str,
                        help='Save current configuration to specified file')
    return parser.parse_args()

def main():
    """Main application entry point"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.input_device is not None:
        config['audio']['input_device'] = args.input_device
    if args.output_device is not None:
        config['audio']['output_device'] = args.output_device
    if args.buffer_size is not None:
        config['audio']['buffer_size'] = args.buffer_size
    if args.sample_rate is not None:
        config['audio']['sample_rate'] = args.sample_rate
    if args.pitch_shift is not None:
        config['transformation']['pitch_shift'] = args.pitch_shift
    if args.formant_shift is not None:
        config['transformation']['formant_shift'] = args.formant_shift
    
    # Save configuration if requested
    if args.save_config:
        with open(args.save_config, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {args.save_config}")
        return
    
    # Set up logging
    logger = setup_logging(config['logging'])
    logger.info("Starting Voice Transformer")
    
    try:
        # Initialize display
        display = Display(refresh_rate_ms=config['ui']['refresh_rate_ms'],
                         show_metrics=config['ui']['show_metrics'],
                         color_output=config['ui']['color_output'])
        
        # Initialize audio components
        audio_input = AudioInput(
            device_index=config['audio']['input_device'],
            sample_rate=config['audio']['sample_rate'],
            buffer_size=config['audio']['buffer_size'],
            channels=config['audio']['channels']
        )
        
        audio_output = AudioOutput(
            device_index=config['audio']['output_device'],
            sample_rate=config['audio']['sample_rate'],
            buffer_size=config['audio']['buffer_size'],
            channels=config['audio']['channels']
        )
        
        audio_processor = AudioProcessor()
        
        # Initialize transformation pipeline
        transformation_pipeline = TransformationPipeline(
            model_path=config['transformation']['model_path'],
            pitch_shift=config['transformation']['pitch_shift'],
            formant_shift=config['transformation']['formant_shift'],
            intensity=config['transformation']['intensity'],
            preserve_tones=config['transformation']['preserve_tones']
        )
        
        # Initialize command handler
        command_handler = CommandHandler(
            audio_input=audio_input,
            audio_output=audio_output,
            transformation_pipeline=transformation_pipeline,
            display=display
        )
        
        # Start the command line interface
        display.welcome()
        command_handler.start_cli()
        
        # Main application loop
        global running
        while running:
            command = input("voice-transformer> ").strip().lower()
            if command in ["exit", "quit", "q"]:
                running = False
            else:
                command_handler.process_command(command)
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        logger.info("Shutting down Voice Transformer")
        if 'audio_input' in locals():
            audio_input.close()
        if 'audio_output' in locals():
            audio_output.close()
        if 'transformation_pipeline' in locals():
            transformation_pipeline.close()
        print("Voice Transformer has been shut down.")

if __name__ == "__main__":
    main() 