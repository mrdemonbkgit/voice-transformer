"""
Audio input module for Voice Transformer
"""

import numpy as np
import pyaudio
import threading
import logging
import time
from collections import deque

logger = logging.getLogger(__name__)

class AudioInput:
    """
    Audio input handler class for capturing microphone input
    """
    
    def __init__(self, device_index=None, sample_rate=16000, buffer_size=512, channels=1):
        """
        Initialize the audio input handler
        
        Args:
            device_index (int, optional): Index of input device. Defaults to None (system default).
            sample_rate (int, optional): Sample rate in Hz. Defaults to 16000.
            buffer_size (int, optional): Buffer size in samples. Defaults to 512.
            channels (int, optional): Number of channels. Defaults to 1 (mono).
        """
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.format = pyaudio.paInt16
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.active = False
        self.data_queue = deque(maxlen=100)  # Store up to 100 audio chunks
        self.lock = threading.Lock()
        
        # Check if the device exists
        if device_index is not None:
            try:
                device_info = self.audio.get_device_info_by_index(device_index)
                logger.info(f"Using input device: {device_info['name']}")
            except IOError:
                logger.warning(f"Input device with index {device_index} not found. Using default device.")
                self.device_index = None
    
    def callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for audio stream
        
        Args:
            in_data (bytes): Input audio data
            frame_count (int): Number of frames
            time_info (dict): Time information
            status (int): Status flag
            
        Returns:
            tuple: (None, pyaudio.paContinue)
        """
        if status:
            logger.warning(f"Audio input status: {status}")
        
        # Convert to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Add to queue
        with self.lock:
            self.data_queue.append(audio_data)
        
        return (None, pyaudio.paContinue)
    
    def start(self):
        """
        Start audio input stream
        """
        if self.stream is not None and self.active:
            logger.warning("Audio input already started")
            return
        
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.buffer_size,
                stream_callback=self.callback
            )
            self.active = True
            logger.info("Audio input started")
        except Exception as e:
            logger.error(f"Error starting audio input: {e}")
            raise
    
    def stop(self):
        """
        Stop audio input stream
        """
        if self.stream is not None and self.active:
            self.stream.stop_stream()
            self.active = False
            logger.info("Audio input stopped")
    
    def close(self):
        """
        Close audio input stream and release resources
        """
        if self.stream is not None:
            self.stop()
            self.stream.close()
            self.stream = None
        
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None
        
        logger.info("Audio input closed")
    
    def get_audio_chunk(self, timeout=0.5):
        """
        Get the next audio chunk from the queue
        
        Args:
            timeout (float, optional): Timeout in seconds. Defaults to 0.5.
            
        Returns:
            numpy.ndarray: Audio data, or None if no data is available
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                if len(self.data_queue) > 0:
                    return self.data_queue.popleft()
            time.sleep(0.01)
        
        logger.warning("Timeout while waiting for audio input")
        return None
    
    def list_devices(self):
        """
        List available audio input devices
        
        Returns:
            list: List of dictionaries with device information
        """
        devices = []
        
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate'])
                })
        
        return devices
        
    def is_active(self):
        """
        Check if the audio input stream is active
        
        Returns:
            bool: True if active, False otherwise
        """
        return self.active 