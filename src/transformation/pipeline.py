"""
Voice transformation pipeline module
"""

import os
import numpy as np
import logging
import time
import threading
from collections import deque

from src.transformation.rvc_model import RVCModel

logger = logging.getLogger(__name__)

class TransformationPipeline:
    """
    Voice transformation pipeline that coordinates the audio processing and transformation
    """
    
    def __init__(self, model_path, pitch_shift=5.0, formant_shift=1.2, intensity=0.8, preserve_tones=True):
        """
        Initialize the transformation pipeline
        
        Args:
            model_path (str): Path to the RVC model file
            pitch_shift (float, optional): Pitch shift in semitones. Defaults to 5.0.
            formant_shift (float, optional): Formant shift factor. Defaults to 1.2.
            intensity (float, optional): Voice conversion intensity. Defaults to 0.8.
            preserve_tones (bool, optional): Whether to preserve tonal variations. Defaults to True.
        """
        self.model_path = model_path
        self.pitch_shift = pitch_shift
        self.formant_shift = formant_shift
        self.intensity = intensity
        self.preserve_tones = preserve_tones
        
        # Initialize the RVC model
        self.model = RVCModel(model_path)
        
        # Processing state
        self.active = False
        self.thread = None
        self.stop_event = threading.Event()
        
        # Buffers for audio processing
        self.input_queue = deque(maxlen=100)
        self.output_queue = deque(maxlen=100)
        self.lock = threading.Lock()
        
        # Performance metrics
        self.processing_times = deque(maxlen=50)  # Last 50 processing times
        self.last_latency = 0
        
        logger.info(f"Transformation pipeline initialized (pitch_shift={pitch_shift}, formant_shift={formant_shift})")
    
    def start(self):
        """
        Start the transformation pipeline
        """
        if self.active:
            logger.warning("Transformation pipeline already running")
            return
        
        # Reset stop event
        self.stop_event.clear()
        
        # Start processing thread
        self.thread = threading.Thread(target=self._processing_loop)
        self.thread.daemon = True
        self.thread.start()
        
        self.active = True
        logger.info("Transformation pipeline started")
    
    def stop(self):
        """
        Stop the transformation pipeline
        """
        if not self.active:
            return
        
        # Signal thread to stop
        self.stop_event.set()
        
        # Wait for thread to terminate
        if self.thread is not None:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        self.active = False
        logger.info("Transformation pipeline stopped")
    
    def close(self):
        """
        Close the transformation pipeline and release resources
        """
        self.stop()
        
        # Unload model
        if self.model is not None:
            self.model.unload()
            self.model = None
        
        logger.info("Transformation pipeline closed")
    
    def add_audio(self, audio_data):
        """
        Add audio data to the input queue for processing
        
        Args:
            audio_data (numpy.ndarray): Audio data to process
        """
        with self.lock:
            self.input_queue.append(audio_data)
    
    def get_transformed_audio(self):
        """
        Get the next chunk of transformed audio from the output queue
        
        Returns:
            numpy.ndarray: Transformed audio data, or None if no data is available
        """
        with self.lock:
            if len(self.output_queue) > 0:
                return self.output_queue.popleft()
            else:
                return None
    
    def _processing_loop(self):
        """
        Main processing loop for the transformation pipeline
        """
        logger.info("Processing loop started")
        
        # Ensure model is loaded
        if not self.model.is_loaded:
            self.model.load()
        
        while not self.stop_event.is_set():
            # Check if there's audio to process
            audio_data = None
            with self.lock:
                if len(self.input_queue) > 0:
                    audio_data = self.input_queue.popleft()
            
            if audio_data is not None:
                try:
                    # Measure processing time
                    start_time = time.time()
                    
                    # Process audio (this is a simplified implementation)
                    # In a real implementation, we would:
                    # 1. Extract audio features
                    # 2. Apply voice conversion
                    # 3. Synthesize transformed audio
                    
                    # Since this is a placeholder, we'll simulate the process
                    # with some dummy operations to show latency measurement
                    
                    # Simulate feature extraction (approximately 10-20ms)
                    time.sleep(0.015)
                    
                    # Simulate voice conversion (approximately 20-50ms)
                    time.sleep(0.035)
                    
                    # Simulate audio synthesis (approximately 10-20ms)
                    time.sleep(0.015)
                    
                    # For demo purposes, we'll just add some noise to the original audio
                    # with a pitch shift effect to simulate transformation
                    transformed_audio = self._simulate_transformation(audio_data)
                    
                    # Add to output queue
                    with self.lock:
                        self.output_queue.append(transformed_audio)
                    
                    # Record processing time
                    end_time = time.time()
                    proc_time = (end_time - start_time) * 1000  # Convert to ms
                    with self.lock:
                        self.processing_times.append(proc_time)
                        self.last_latency = proc_time
                    
                except Exception as e:
                    logger.error(f"Error processing audio: {e}")
            
            # Sleep a bit to prevent CPU overuse
            time.sleep(0.001)
        
        logger.info("Processing loop stopped")
    
    def _simulate_transformation(self, audio_data):
        """
        Simulate voice transformation for demonstration purposes
        
        Args:
            audio_data (numpy.ndarray): Input audio data
            
        Returns:
            numpy.ndarray: Simulated transformed audio
        """
        # Convert to float if necessary
        if audio_data.dtype != np.float32:
            audio_float = audio_data.astype(np.float32) / 32768.0
        else:
            audio_float = audio_data.copy()
        
        # Simple pitch shift simulation using resampling
        # (Not a realistic pitch shift, just for demonstration)
        pitch_factor = 2 ** (self.pitch_shift / 12.0)
        # Stretch audio by pitch factor
        indices = np.round(np.arange(0, len(audio_float), pitch_factor)).astype(int)
        indices = indices[indices < len(audio_float)]
        
        # Simple artificial formant shift by adding harmonics
        # (Not a realistic formant shift, just for demonstration)
        formant_shift = np.sin(np.arange(len(indices)) * 0.1 * self.formant_shift) * 0.1
        
        # Create transformed audio
        transformed = audio_float[indices] + formant_shift
        
        # Normalize
        transformed = np.clip(transformed, -0.99, 0.99)
        
        # Convert back to int16
        return (transformed * 32767).astype(np.int16)
    
    def get_metrics(self):
        """
        Get performance metrics for the transformation pipeline
        
        Returns:
            dict: Dictionary of performance metrics
        """
        with self.lock:
            if len(self.processing_times) > 0:
                avg_latency = sum(self.processing_times) / len(self.processing_times)
                max_latency = max(self.processing_times)
                min_latency = min(self.processing_times)
                current_latency = self.last_latency
            else:
                avg_latency = 0
                max_latency = 0
                min_latency = 0
                current_latency = 0
            
            input_queue_len = len(self.input_queue)
            output_queue_len = len(self.output_queue)
        
        return {
            'avg_latency_ms': avg_latency,
            'max_latency_ms': max_latency,
            'min_latency_ms': min_latency,
            'current_latency_ms': current_latency,
            'input_queue_len': input_queue_len,
            'output_queue_len': output_queue_len,
            'is_active': self.active
        }
    
    def update_parameters(self, pitch_shift=None, formant_shift=None, intensity=None, preserve_tones=None):
        """
        Update transformation parameters
        
        Args:
            pitch_shift (float, optional): Pitch shift in semitones. Defaults to None (no change).
            formant_shift (float, optional): Formant shift factor. Defaults to None (no change).
            intensity (float, optional): Voice conversion intensity. Defaults to None (no change).
            preserve_tones (bool, optional): Whether to preserve tonal variations. Defaults to None (no change).
        """
        if pitch_shift is not None:
            self.pitch_shift = pitch_shift
        
        if formant_shift is not None:
            self.formant_shift = formant_shift
        
        if intensity is not None:
            self.intensity = intensity
        
        if preserve_tones is not None:
            self.preserve_tones = preserve_tones
        
        logger.info(f"Parameters updated: pitch_shift={self.pitch_shift}, formant_shift={self.formant_shift}, "
                  f"intensity={self.intensity}, preserve_tones={self.preserve_tones}")
    
    def is_active(self):
        """
        Check if the transformation pipeline is active
        
        Returns:
            bool: True if active, False otherwise
        """
        return self.active 