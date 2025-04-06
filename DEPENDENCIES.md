# Dependencies

## Core Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | >=3.8, <3.11 | Programming language |
| PyAudio | 0.2.13 | Audio input/output handling |
| NumPy | 1.24.3 | Audio data manipulation |
| librosa | 0.10.1 | Audio analysis and processing |
| PyTorch | 2.0.1 | Machine learning framework for RVC |
| sounddevice | 0.4.6 | Real-time audio playback |
| RVC | - | Voice conversion model |

## RVC Model Requirements

The application uses the RVC (Retrieval-based Voice Conversion) model for voice transformation:

- Pre-trained female voice model for Vietnamese language
- Model file size: ~300MB
- Inference compatible with CPU (GPU optional for improved performance)
- 16-bit float precision for efficient inference

## Development Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| pytest | 7.3.1 | Testing framework |
| black | 23.3.0 | Code formatting |
| pylint | 2.17.4 | Code linting |
| setuptools | 67.8.0 | Package building |

## System Requirements

### Minimum Hardware Requirements
- CPU: 2.0+ GHz dual-core processor
- RAM: 4GB (8GB recommended)
- Storage: 500MB for application and models
- Audio: Working microphone and speakers/headphones

### Operating System
- Windows 10 or later
- 64-bit OS required

## Installation Tools
- pip (Python package installer)
- Git (for source code management)

## Runtime Environment
The application runs as a command-line interface (CLI) application in the Windows Command Prompt or PowerShell terminal. 