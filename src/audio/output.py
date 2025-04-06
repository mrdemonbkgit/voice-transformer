"""
Audio output module for Voice Transformer
"""

import numpy as np
import pyaudio
import threading
import logging
import time
from collections import deque

logger = logging.getLogger(__name__)

class AudioOutput:
    """
    Audio output handler class for playing transformed audio
    """
    
    def __init__(self, device_index=None, sample_rate=16000, buffer_size=512, channels=1):
        """
        Initialize the audio output handler
        
        Args:
            device_index (int, optional): Index of output device. Defaults to None (system default).
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
                logger.info(f"Using output device: {device_info['name']}")
            except IOError:
                logger.warning(f"Output device with index {device_index} not found. Using default device.")
                self.device_index = None
    
    def callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for audio stream
        
        Args:
            in_data (bytes): Not used for output stream
            frame_count (int): Number of frames to output
            time_info (dict): Time information
            status (int): Status flag
            
        Returns:
            tuple: (audio_data, pyaudio.paContinue)
        """
        if status:
            logger.warning(f"Audio output status: {status}")
        
        # Get audio data from queue
        with self.lock:
            if len(self.data_queue) > 0:
                audio_data = self.data_queue.popleft()
                # If the audio data is shorter than requested, pad with zeros
                if len(audio_data) < frame_count:
                    audio_data = np.pad(audio_data, (0, frame_count - len(audio_data)), 'constant')
                # If the audio data is longer than requested, truncate
                elif len(audio_data) > frame_count:
                    audio_data = audio_data[:frame_count]
                
                return (audio_data.tobytes(), pyaudio.paContinue)
            else:
                # No data available, output silence
                return (np.zeros(frame_count, dtype=np.int16).tobytes(), pyaudio.paContinue)
    
    def start(self):
        """
        Start audio output stream
        """
        if self.stream is not None and self.active:
            logger.warning("Audio output already started")
            return
        
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.device_index,
                frames_per_buffer=self.buffer_size,
                stream_callback=self.callback
            )
            self.active = True
            logger.info("Audio output started")
        except Exception as e:
            logger.error(f"Error starting audio output: {e}")
            raise
    
    def stop(self):
        """
        Stop audio output stream
        """
        if self.stream is not None and self.active:
            self.stream.stop_stream()
            self.active = False
            logger.info("Audio output stopped")
    
    def close(self):
        """
        Close audio output stream and release resources
        """
        if self.stream is not None:
            self.stop()
            self.stream.close()
            self.stream = None
        
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None
        
        logger.info("Audio output closed")
    
    def play_audio(self, audio_data):
        """
        Queue audio data for playback
        
        Args:
            audio_data (numpy.ndarray): Audio data to play
        """
        with self.lock:
            self.data_queue.append(audio_data)
    
    def list_devices(self):
        """
        List available audio output devices
        
        Returns:
            list: List of dictionaries with device information
        """
        devices = []
        
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxOutputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate'])
                })
        
        return devices
        
    def is_active(self):
        """
        Check if the audio output stream is active
        
        Returns:
            bool: True if active, False otherwise
        """
        return self.active
    
    def get_queue_length(self):
        """
        Get the current length of the output queue
        
        Returns:
            int: Number of audio chunks in queue
        """
        with self.lock:
            return len(self.data_queue) 