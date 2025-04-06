"""
Command handler module for Voice Transformer
"""

import logging
import threading
import time

logger = logging.getLogger(__name__)

class CommandHandler:
    """
    Command handler for Voice Transformer CLI
    """
    
    def __init__(self, audio_input, audio_output, transformation_pipeline, display):
        """
        Initialize the command handler
        
        Args:
            audio_input: Audio input handler
            audio_output: Audio output handler
            transformation_pipeline: Transformation pipeline
            display: Display handler
        """
        self.audio_input = audio_input
        self.audio_output = audio_output
        self.pipeline = transformation_pipeline
        self.display = display
        
        # Processing state
        self.active = False
        self.paused = False
        self.thread = None
        self.stop_event = threading.Event()
        
        logger.info("Command handler initialized")
    
    def start_cli(self):
        """
        Start the command-line interface
        """
        # Show help information
        self.display.help()
    
    def process_command(self, command):
        """
        Process a command from the user
        
        Args:
            command (str): Command string
        """
        # Split command and arguments
        parts = command.strip().split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            if cmd == "help":
                self.display.help()
            
            elif cmd == "start":
                self._start_transformation()
            
            elif cmd == "stop":
                self._stop_transformation()
            
            elif cmd == "pause":
                self._pause_transformation()
            
            elif cmd == "resume":
                self._resume_transformation()
            
            elif cmd == "devices":
                self._list_devices()
            
            elif cmd == "input":
                self._set_input_device(args)
            
            elif cmd == "output":
                self._set_output_device(args)
            
            elif cmd == "pitch":
                self._set_pitch_shift(args)
            
            elif cmd == "formant":
                self._set_formant_shift(args)
            
            elif cmd == "metrics":
                self._toggle_metrics()
            
            elif cmd == "status":
                self._show_status()
            
            else:
                self.display.error(f"Unknown command: {cmd}")
                self.display.help()
        
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.display.error(f"Error: {e}")
    
    def _start_transformation(self):
        """
        Start voice transformation
        """
        if self.active:
            if self.paused:
                self._resume_transformation()
            else:
                self.display.info("Voice transformation is already running")
            return
        
        try:
            # Start audio input
            self.audio_input.start()
            
            # Start audio output
            self.audio_output.start()
            
            # Start transformation pipeline
            self.pipeline.start()
            
            # Start audio processing thread
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._processing_loop)
            self.thread.daemon = True
            self.thread.start()
            
            # Start metrics display
            self.display.start_metrics()
            
            self.active = True
            self.paused = False
            
            logger.info("Voice transformation started")
            self.display.success("Voice transformation started")
        
        except Exception as e:
            logger.error(f"Error starting voice transformation: {e}")
            self.display.error(f"Failed to start voice transformation: {e}")
            self._cleanup()
    
    def _stop_transformation(self):
        """
        Stop voice transformation
        """
        if not self.active:
            self.display.info("Voice transformation is not running")
            return
        
        try:
            # Stop processing thread
            self.stop_event.set()
            if self.thread is not None:
                self.thread.join(timeout=2.0)
                self.thread = None
            
            # Stop audio components
            self.audio_input.stop()
            self.audio_output.stop()
            self.pipeline.stop()
            
            # Stop metrics display
            self.display.stop_metrics()
            
            self.active = False
            self.paused = False
            
            logger.info("Voice transformation stopped")
            self.display.success("Voice transformation stopped")
        
        except Exception as e:
            logger.error(f"Error stopping voice transformation: {e}")
            self.display.error(f"Error stopping voice transformation: {e}")
    
    def _pause_transformation(self):
        """
        Pause voice transformation
        """
        if not self.active:
            self.display.error("Voice transformation is not running")
            return
        
        if self.paused:
            self.display.info("Voice transformation is already paused")
            return
        
        try:
            # Stop audio components but keep the processing thread
            self.audio_input.stop()
            self.audio_output.stop()
            
            self.paused = True
            
            logger.info("Voice transformation paused")
            self.display.success("Voice transformation paused")
        
        except Exception as e:
            logger.error(f"Error pausing voice transformation: {e}")
            self.display.error(f"Error pausing voice transformation: {e}")
    
    def _resume_transformation(self):
        """
        Resume voice transformation after pause
        """
        if not self.active:
            self._start_transformation()
            return
        
        if not self.paused:
            self.display.info("Voice transformation is not paused")
            return
        
        try:
            # Restart audio components
            self.audio_input.start()
            self.audio_output.start()
            
            self.paused = False
            
            logger.info("Voice transformation resumed")
            self.display.success("Voice transformation resumed")
        
        except Exception as e:
            logger.error(f"Error resuming voice transformation: {e}")
            self.display.error(f"Error resuming voice transformation: {e}")
    
    def _list_devices(self):
        """
        List available audio devices
        """
        input_devices = self.audio_input.list_devices()
        output_devices = self.audio_output.list_devices()
        
        self.display.show_devices(input_devices, output_devices)
    
    def _set_input_device(self, args):
        """
        Set input device
        
        Args:
            args (list): Command arguments
        """
        if not args:
            self.display.error("Please specify an input device ID")
            return
        
        try:
            device_id = int(args[0])
            
            # Get available devices to check if the ID is valid
            devices = self.audio_input.list_devices()
            device_ids = [device['index'] for device in devices]
            
            if device_id not in device_ids:
                self.display.error(f"Invalid device ID: {device_id}")
                return
            
            # Check if transformation is running
            was_active = self.active
            
            # Stop if active
            if was_active:
                self._stop_transformation()
            
            # Set new device
            self.audio_input = type(self.audio_input)(
                device_index=device_id,
                sample_rate=self.audio_input.sample_rate,
                buffer_size=self.audio_input.buffer_size,
                channels=self.audio_input.channels
            )
            
            # Restart if it was active
            if was_active:
                self._start_transformation()
            
            device_name = next((device['name'] for device in devices if device['index'] == device_id), "Unknown")
            logger.info(f"Input device set to {device_id} ({device_name})")
            self.display.success(f"Input device set to: {device_name}")
        
        except ValueError:
            self.display.error("Device ID must be a number")
        except Exception as e:
            logger.error(f"Error setting input device: {e}")
            self.display.error(f"Error setting input device: {e}")
    
    def _set_output_device(self, args):
        """
        Set output device
        
        Args:
            args (list): Command arguments
        """
        if not args:
            self.display.error("Please specify an output device ID")
            return
        
        try:
            device_id = int(args[0])
            
            # Get available devices to check if the ID is valid
            devices = self.audio_output.list_devices()
            device_ids = [device['index'] for device in devices]
            
            if device_id not in device_ids:
                self.display.error(f"Invalid device ID: {device_id}")
                return
            
            # Check if transformation is running
            was_active = self.active
            
            # Stop if active
            if was_active:
                self._stop_transformation()
            
            # Set new device
            self.audio_output = type(self.audio_output)(
                device_index=device_id,
                sample_rate=self.audio_output.sample_rate,
                buffer_size=self.audio_output.buffer_size,
                channels=self.audio_output.channels
            )
            
            # Restart if it was active
            if was_active:
                self._start_transformation()
            
            device_name = next((device['name'] for device in devices if device['index'] == device_id), "Unknown")
            logger.info(f"Output device set to {device_id} ({device_name})")
            self.display.success(f"Output device set to: {device_name}")
        
        except ValueError:
            self.display.error("Device ID must be a number")
        except Exception as e:
            logger.error(f"Error setting output device: {e}")
            self.display.error(f"Error setting output device: {e}")
    
    def _set_pitch_shift(self, args):
        """
        Set pitch shift
        
        Args:
            args (list): Command arguments
        """
        if not args:
            self.display.error("Please specify a pitch shift value")
            return
        
        try:
            pitch_shift = float(args[0])
            
            # Validate range
            if pitch_shift < -12.0 or pitch_shift > 12.0:
                self.display.error("Pitch shift must be between -12.0 and 12.0 semitones")
                return
            
            # Update pipeline parameters
            self.pipeline.update_parameters(pitch_shift=pitch_shift)
            
            logger.info(f"Pitch shift set to {pitch_shift}")
            self.display.success(f"Pitch shift set to {pitch_shift} semitones")
        
        except ValueError:
            self.display.error("Pitch shift must be a number")
        except Exception as e:
            logger.error(f"Error setting pitch shift: {e}")
            self.display.error(f"Error setting pitch shift: {e}")
    
    def _set_formant_shift(self, args):
        """
        Set formant shift
        
        Args:
            args (list): Command arguments
        """
        if not args:
            self.display.error("Please specify a formant shift value")
            return
        
        try:
            formant_shift = float(args[0])
            
            # Validate range
            if formant_shift < 0.5 or formant_shift > 2.0:
                self.display.error("Formant shift must be between 0.5 and 2.0")
                return
            
            # Update pipeline parameters
            self.pipeline.update_parameters(formant_shift=formant_shift)
            
            logger.info(f"Formant shift set to {formant_shift}")
            self.display.success(f"Formant shift set to {formant_shift}")
        
        except ValueError:
            self.display.error("Formant shift must be a number")
        except Exception as e:
            logger.error(f"Error setting formant shift: {e}")
            self.display.error(f"Error setting formant shift: {e}")
    
    def _toggle_metrics(self):
        """
        Toggle performance metrics display
        """
        self.display.show_metrics = not self.display.show_metrics
        
        if self.display.show_metrics:
            if self.active and not self.display.active:
                self.display.start_metrics()
            self.display.info("Performance metrics display enabled")
        else:
            if self.display.active:
                self.display.stop_metrics()
            self.display.info("Performance metrics display disabled")
    
    def _show_status(self):
        """
        Show current status information
        """
        self.display.show_status(self.audio_input, self.audio_output, self.pipeline)
    
    def _processing_loop(self):
        """
        Main processing loop for voice transformation
        """
        logger.info("Processing loop started")
        
        while not self.stop_event.is_set():
            if self.active and not self.paused:
                try:
                    # Get audio from input
                    audio_data = self.audio_input.get_audio_chunk()
                    
                    if audio_data is not None:
                        # Add to pipeline for processing
                        self.pipeline.add_audio(audio_data)
                        
                        # Get processed audio from pipeline
                        transformed_audio = self.pipeline.get_transformed_audio()
                        
                        if transformed_audio is not None:
                            # Send to output
                            self.audio_output.play_audio(transformed_audio)
                    
                    # Update metrics
                    self.display.update_metrics(self.pipeline.get_metrics())
                
                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
            
            # Sleep a bit to prevent CPU overuse
            time.sleep(0.001)
        
        logger.info("Processing loop stopped")
    
    def _cleanup(self):
        """
        Clean up resources
        """
        try:
            # Stop processing thread
            self.stop_event.set()
            if self.thread is not None:
                self.thread.join(timeout=2.0)
                self.thread = None
            
            # Stop audio components
            if hasattr(self, 'audio_input'):
                self.audio_input.stop()
            
            if hasattr(self, 'audio_output'):
                self.audio_output.stop()
            
            if hasattr(self, 'pipeline'):
                self.pipeline.stop()
            
            # Stop metrics display
            if hasattr(self, 'display'):
                self.display.stop_metrics()
            
            self.active = False
            self.paused = False
            
            logger.info("Resources cleaned up")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            if hasattr(self, 'display'):
                self.display.error(f"Error during cleanup: {e}") 