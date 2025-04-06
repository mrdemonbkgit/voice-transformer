"""
CLI display module for Voice Transformer
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class Display:
    """
    CLI display handler for Voice Transformer
    """
    
    def __init__(self, refresh_rate_ms=250, show_metrics=True, color_output=True):
        """
        Initialize the display handler
        
        Args:
            refresh_rate_ms (int, optional): Refresh rate in milliseconds. Defaults to 250.
            show_metrics (bool, optional): Whether to show performance metrics. Defaults to True.
            color_output (bool, optional): Whether to use colored output. Defaults to True.
        """
        self.refresh_rate_ms = refresh_rate_ms
        self.show_metrics = show_metrics
        self.color_output = color_output
        
        # Colors for terminal output (ANSI escape codes)
        if self.color_output and os.name != 'nt':  # ANSI colors don't work well in Windows CMD
            self.COLORS = {
                'RESET': '\033[0m',
                'RED': '\033[91m',
                'GREEN': '\033[92m',
                'YELLOW': '\033[93m',
                'BLUE': '\033[94m',
                'MAGENTA': '\033[95m',
                'CYAN': '\033[96m',
                'WHITE': '\033[97m',
                'BOLD': '\033[1m',
                'UNDERLINE': '\033[4m'
            }
        else:
            self.COLORS = {k: '' for k in ['RESET', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', 'BOLD', 'UNDERLINE']}
        
        # Display state
        self.active = False
        self.thread = None
        self.stop_event = threading.Event()
        
        # Metrics
        self.metrics = {}
        self.metrics_lock = threading.Lock()
        
        logger.info("Display initialized")
    
    def welcome(self):
        """
        Display welcome message
        """
        print(f"\n{self.COLORS['BOLD']}{self.COLORS['CYAN']}Voice Transformer{self.COLORS['RESET']}")
        print(f"{self.COLORS['BOLD']}Real-time male to female voice transformation{self.COLORS['RESET']}")
        print(f"Optimized for Vietnamese language\n")
        print(f"Type {self.COLORS['YELLOW']}help{self.COLORS['RESET']} for a list of commands.\n")
    
    def help(self):
        """
        Display help information
        """
        print(f"\n{self.COLORS['BOLD']}Available Commands:{self.COLORS['RESET']}")
        print(f"  {self.COLORS['YELLOW']}start{self.COLORS['RESET']}         - Start voice transformation")
        print(f"  {self.COLORS['YELLOW']}stop{self.COLORS['RESET']}          - Stop voice transformation")
        print(f"  {self.COLORS['YELLOW']}pause{self.COLORS['RESET']}         - Temporarily pause transformation")
        print(f"  {self.COLORS['YELLOW']}resume{self.COLORS['RESET']}        - Resume after pause")
        print(f"  {self.COLORS['YELLOW']}devices{self.COLORS['RESET']}       - List available audio devices")
        print(f"  {self.COLORS['YELLOW']}input <id>{self.COLORS['RESET']}    - Set input device by ID")
        print(f"  {self.COLORS['YELLOW']}output <id>{self.COLORS['RESET']}   - Set output device by ID")
        print(f"  {self.COLORS['YELLOW']}pitch <value>{self.COLORS['RESET']} - Set pitch shift (semitones, default: 5.0)")
        print(f"  {self.COLORS['YELLOW']}formant <value>{self.COLORS['RESET']} - Set formant shift (factor, default: 1.2)")
        print(f"  {self.COLORS['YELLOW']}metrics{self.COLORS['RESET']}       - Toggle performance metrics display")
        print(f"  {self.COLORS['YELLOW']}status{self.COLORS['RESET']}        - Show current status")
        print(f"  {self.COLORS['YELLOW']}help{self.COLORS['RESET']}          - Show this help information")
        print(f"  {self.COLORS['YELLOW']}exit{self.COLORS['RESET']} or {self.COLORS['YELLOW']}quit{self.COLORS['RESET']} - Exit the application\n")
    
    def start_metrics(self):
        """
        Start metrics display thread
        """
        if self.active:
            return
        
        # Reset stop event
        self.stop_event.clear()
        
        # Start display thread
        self.thread = threading.Thread(target=self._metrics_loop)
        self.thread.daemon = True
        self.thread.start()
        
        self.active = True
        logger.info("Metrics display started")
    
    def stop_metrics(self):
        """
        Stop metrics display thread
        """
        if not self.active:
            return
        
        # Signal thread to stop
        self.stop_event.set()
        
        # Wait for thread to terminate
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        self.active = False
        logger.info("Metrics display stopped")
    
    def update_metrics(self, metrics):
        """
        Update performance metrics
        
        Args:
            metrics (dict): Dictionary of performance metrics
        """
        with self.metrics_lock:
            self.metrics = metrics
    
    def _metrics_loop(self):
        """
        Main loop for metrics display
        """
        while not self.stop_event.is_set():
            if self.show_metrics:
                self._display_metrics()
            
            # Sleep until next refresh
            time.sleep(self.refresh_rate_ms / 1000.0)
    
    def _display_metrics(self):
        """
        Display performance metrics
        """
        with self.metrics_lock:
            if not self.metrics:
                return
            
            # Clear previous line
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            
            # Display metrics
            latency = self.metrics.get('current_latency_ms', 0)
            if latency > 80:
                latency_color = self.COLORS['RED']
            elif latency > 40:
                latency_color = self.COLORS['YELLOW']
            else:
                latency_color = self.COLORS['GREEN']
            
            status = "ACTIVE" if self.metrics.get('is_active', False) else "STOPPED"
            status_color = self.COLORS['GREEN'] if status == "ACTIVE" else self.COLORS['RED']
            
            sys.stdout.write(f"\rStatus: {status_color}{status}{self.COLORS['RESET']} | ")
            sys.stdout.write(f"Latency: {latency_color}{latency:.1f}ms{self.COLORS['RESET']} | ")
            sys.stdout.write(f"Buffers: {self.metrics.get('input_queue_len', 0)}/{self.metrics.get('output_queue_len', 0)}")
            
            sys.stdout.flush()
    
    def show_status(self, audio_input, audio_output, pipeline):
        """
        Display current status information
        
        Args:
            audio_input: Audio input handler
            audio_output: Audio output handler
            pipeline: Transformation pipeline
        """
        print(f"\n{self.COLORS['BOLD']}Current Status:{self.COLORS['RESET']}")
        
        # Audio input/output status
        input_status = "ACTIVE" if audio_input.is_active() else "STOPPED"
        input_color = self.COLORS['GREEN'] if input_status == "ACTIVE" else self.COLORS['RED']
        
        output_status = "ACTIVE" if audio_output.is_active() else "STOPPED"
        output_color = self.COLORS['GREEN'] if output_status == "ACTIVE" else self.COLORS['RED']
        
        pipeline_status = "ACTIVE" if pipeline.is_active() else "STOPPED"
        pipeline_color = self.COLORS['GREEN'] if pipeline_status == "ACTIVE" else self.COLORS['RED']
        
        print(f"Audio Input: {input_color}{input_status}{self.COLORS['RESET']}")
        print(f"Audio Output: {output_color}{output_status}{self.COLORS['RESET']}")
        print(f"Transformation: {pipeline_color}{pipeline_status}{self.COLORS['RESET']}")
        
        # Transformation parameters
        print(f"\n{self.COLORS['BOLD']}Transformation Parameters:{self.COLORS['RESET']}")
        print(f"Pitch Shift: {self.COLORS['CYAN']}{pipeline.pitch_shift:.1f}{self.COLORS['RESET']} semitones")
        print(f"Formant Shift: {self.COLORS['CYAN']}{pipeline.formant_shift:.1f}{self.COLORS['RESET']}x")
        print(f"Intensity: {self.COLORS['CYAN']}{pipeline.intensity:.1f}{self.COLORS['RESET']}")
        print(f"Preserve Tones: {self.COLORS['CYAN']}{pipeline.preserve_tones}{self.COLORS['RESET']}")
        
        # Performance metrics
        metrics = pipeline.get_metrics()
        print(f"\n{self.COLORS['BOLD']}Performance Metrics:{self.COLORS['RESET']}")
        print(f"Average Latency: {self.COLORS['CYAN']}{metrics.get('avg_latency_ms', 0):.1f}{self.COLORS['RESET']} ms")
        print(f"Current Latency: {self.COLORS['CYAN']}{metrics.get('current_latency_ms', 0):.1f}{self.COLORS['RESET']} ms")
        print(f"Input Buffer: {self.COLORS['CYAN']}{metrics.get('input_queue_len', 0)}{self.COLORS['RESET']} chunks")
        print(f"Output Buffer: {self.COLORS['CYAN']}{metrics.get('output_queue_len', 0)}{self.COLORS['RESET']} chunks")
        
        print()  # Extra newline at the end
    
    def show_devices(self, input_devices, output_devices):
        """
        Display available audio devices
        
        Args:
            input_devices (list): List of input devices
            output_devices (list): List of output devices
        """
        print(f"\n{self.COLORS['BOLD']}Available Audio Devices:{self.COLORS['RESET']}")
        
        print(f"\n{self.COLORS['BOLD']}Input Devices:{self.COLORS['RESET']}")
        for device in input_devices:
            print(f"  [{self.COLORS['CYAN']}{device['index']}{self.COLORS['RESET']}] {device['name']} "
                  f"({device['channels']} channels, {device['sample_rate']} Hz)")
        
        print(f"\n{self.COLORS['BOLD']}Output Devices:{self.COLORS['RESET']}")
        for device in output_devices:
            print(f"  [{self.COLORS['CYAN']}{device['index']}{self.COLORS['RESET']}] {device['name']} "
                  f"({device['channels']} channels, {device['sample_rate']} Hz)")
        
        print(f"\nUse {self.COLORS['YELLOW']}input <id>{self.COLORS['RESET']} or {self.COLORS['YELLOW']}output <id>{self.COLORS['RESET']} to select a device.\n")
    
    def error(self, message):
        """
        Display error message
        
        Args:
            message (str): Error message
        """
        print(f"\n{self.COLORS['RED']}Error: {message}{self.COLORS['RESET']}\n")
    
    def success(self, message):
        """
        Display success message
        
        Args:
            message (str): Success message
        """
        print(f"\n{self.COLORS['GREEN']}{message}{self.COLORS['RESET']}\n")
    
    def info(self, message):
        """
        Display info message
        
        Args:
            message (str): Info message
        """
        print(f"\n{self.COLORS['CYAN']}{message}{self.COLORS['RESET']}\n")
    
    def prompt(self):
        """
        Display command prompt
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        return f"{self.COLORS['BOLD']}[{timestamp}]{self.COLORS['RESET']} > " 