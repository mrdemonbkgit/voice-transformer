"""
Audio processing module for Voice Transformer
"""

import numpy as np
import librosa
import logging
from scipy import signal

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Audio processor class for preprocessing audio data before transformation
    """
    
    def __init__(self, sample_rate=16000, normalize=True, noise_reduction=True):
        """
        Initialize the audio processor
        
        Args:
            sample_rate (int, optional): Sample rate in Hz. Defaults to 16000.
            normalize (bool, optional): Whether to normalize audio. Defaults to True.
            noise_reduction (bool, optional): Whether to apply noise reduction. Defaults to True.
        """
        self.sample_rate = sample_rate
        self.normalize = normalize
        self.noise_reduction = noise_reduction
        
        # Noise profile (will be updated during runtime)
        self.noise_profile = None
        self.noise_threshold = 0.01
        
        logger.info(f"Audio processor initialized (normalize={normalize}, noise_reduction={noise_reduction})")
    
    def process(self, audio_data):
        """
        Process audio data
        
        Args:
            audio_data (numpy.ndarray): Raw audio data (int16)
            
        Returns:
            numpy.ndarray: Processed audio data (float32 normalized to [-1, 1])
        """
        # Convert to float32
        audio_float = audio_data.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
        
        # Apply preprocessing
        if self.normalize:
            audio_float = self._normalize_audio(audio_float)
        
        if self.noise_reduction and self.noise_profile is not None:
            audio_float = self._reduce_noise(audio_float)
        
        return audio_float
    
    def postprocess(self, audio_data):
        """
        Post-process audio data after transformation
        
        Args:
            audio_data (numpy.ndarray): Transformed audio data (float32 in [-1, 1])
            
        Returns:
            numpy.ndarray: Processed audio data (int16)
        """
        # Ensure audio is within [-1, 1] range
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Convert back to int16
        audio_int = (audio_data * 32767).astype(np.int16)
        
        return audio_int
    
    def _normalize_audio(self, audio_data):
        """
        Normalize audio volume
        
        Args:
            audio_data (numpy.ndarray): Audio data
            
        Returns:
            numpy.ndarray: Normalized audio data
        """
        # Get maximum amplitude
        max_amp = np.max(np.abs(audio_data))
        
        # Only normalize if the maximum amplitude is not too small
        if max_amp > 0.01:
            # Normalize to 70% of maximum possible amplitude
            target_amp = 0.7
            gain = target_amp / max_amp
            normalized_audio = audio_data * gain
            return normalized_audio
        else:
            # Audio is very quiet, possibly silence
            return audio_data
    
    def update_noise_profile(self, audio_data):
        """
        Update noise profile from audio data (assumed to be background noise)
        
        Args:
            audio_data (numpy.ndarray): Audio data containing background noise
        """
        if np.max(np.abs(audio_data)) < self.noise_threshold:
            # Convert to float if not already
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            # Compute noise profile (spectral characteristics)
            self.noise_profile = np.mean(np.abs(librosa.stft(audio_data)), axis=1)
            logger.info("Noise profile updated")
    
    def _reduce_noise(self, audio_data):
        """
        Apply simple spectral subtraction for noise reduction
        
        Args:
            audio_data (numpy.ndarray): Audio data
            
        Returns:
            numpy.ndarray: Noise-reduced audio data
        """
        # Simple spectral subtraction
        stft = librosa.stft(audio_data)
        stft_mag = np.abs(stft)
        stft_phase = np.angle(stft)
        
        # Subtract noise profile with a noise gate
        noise_gate = 2.0
        stft_mag_reduced = np.maximum(stft_mag - self.noise_profile[:, np.newaxis] * noise_gate, 0)
        
        # Reconstruct signal
        stft_reduced = stft_mag_reduced * np.exp(1j * stft_phase)
        audio_reduced = librosa.istft(stft_reduced, length=len(audio_data))
        
        return audio_reduced
    
    def extract_features(self, audio_data):
        """
        Extract audio features for voice transformation
        
        Args:
            audio_data (numpy.ndarray): Processed audio data
            
        Returns:
            dict: Dictionary of audio features including:
                - fundamental_frequency: F0 contour
                - spectral_envelope: Spectral envelope
                - harmonic_components: Harmonic components
                - aperiodic_components: Aperiodic components
        """
        # Extract fundamental frequency (F0)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio_data, 
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C6'),
            sr=self.sample_rate
        )
        
        # Extract spectral envelope
        spec = np.abs(librosa.stft(audio_data))
        
        # Simple harmonic-percussive source separation
        harmonic, percussive = librosa.decompose.hpss(spec)
        
        return {
            'fundamental_frequency': f0,
            'voiced_flag': voiced_flag,
            'spectral_envelope': spec,
            'harmonic_components': harmonic,
            'aperiodic_components': percussive
        } 