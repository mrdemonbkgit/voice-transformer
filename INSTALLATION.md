# Installation Guide

## Prerequisites
Before installing Voice Transformer, ensure you have the following prerequisites:

- Windows 10 or later (64-bit)
- Python 3.8-3.10 installed
- Working microphone (built-in or external)
- Speakers or headphones
- Administrator privileges (for installing Python packages)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/mrdemonbkgit/voice-transformer.git
cd voice-transformer
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
This will install all required Python packages listed in the `requirements.txt` file.

### 4. Download the RVC Model
```bash
python scripts/download_model.py
```
This script will download the pre-trained Vietnamese female voice model (~300MB) to the appropriate directory.

### 5. Verify Installation
```bash
python scripts/test_audio.py
```
This will test your audio input/output devices to ensure they're configured correctly.

## Troubleshooting

### PyAudio Installation Issues
If you encounter problems installing PyAudio, you may need to install it manually:

1. Download the appropriate PyAudio wheel file for your Python version from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. Install the wheel file:
```bash
pip install [downloaded-wheel-file].whl
```

### Audio Device Not Detected
If your microphone or speakers are not being detected:

1. Ensure they are connected and working in other applications
2. Run:
```bash
python scripts/list_audio_devices.py
```
3. Note the device index of your microphone and update the configuration file

### Model Download Fails
If the model download fails:

1. Download manually from the backup link provided in the error message
2. Place the model file in the `models/` directory
3. Verify with:
```bash
python scripts/verify_model.py
```

## Configuration

After installation, you can modify settings in the `config.json` file:

- `input_device`: Set to the index of your preferred microphone
- `output_device`: Set to the index of your preferred audio output
- `buffer_size`: Adjust if you experience audio stuttering (higher = more latency but fewer dropouts)
- `model_parameters`: Fine-tune the voice transformation parameters

## Updating

To update to the latest version:

```bash
git pull
pip install -r requirements.txt
``` 