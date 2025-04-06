# Usage Guide

## Starting the Application

1. Open Command Prompt or PowerShell
2. Navigate to the voice-transformer directory
3. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
4. Run the application:
   ```
   python voice_transformer.py
   ```

## Basic Commands

The Voice Transformer provides a simple command-line interface with the following commands:

| Command | Description |
|---------|-------------|
| `start` | Start voice transformation |
| `stop` | Stop voice transformation |
| `pause` | Temporarily pause transformation |
| `resume` | Resume after pause |
| `exit` or `quit` | Exit the application |
| `help` | Display help information |

## Configuration Options

You can provide configuration options when starting the application:

```
python voice_transformer.py --input-device 1 --output-device 2 --buffer-size 1024
```

| Option | Description | Default |
|--------|-------------|---------|
| `--input-device` | Microphone device index | System default |
| `--output-device` | Speaker device index | System default |
| `--buffer-size` | Audio buffer size (samples) | 512 |
| `--sample-rate` | Audio sample rate (Hz) | 16000 |
| `--pitch-shift` | Voice pitch adjustment (semitones) | 5.0 |
| `--formant-shift` | Formant shift factor | 1.2 |
| `--config` | Path to configuration file | config.json |

## Real-time Controls

While the application is running, you can use the following keyboard commands:

| Key | Function |
|-----|----------|
| `+` | Increase pitch shift |
| `-` | Decrease pitch shift |
| `[` | Increase formant shift |
| `]` | Decrease formant shift |
| `p` | Toggle pause/resume |
| `q` | Quit application |

## Monitoring Performance

The application displays real-time performance metrics:

- **CPU Usage**: Percentage of CPU being used
- **Latency**: Current audio processing latency in milliseconds
- **Buffer**: Number of audio samples in buffer

If latency increases too much:
1. Try increasing the buffer size
2. Close other CPU-intensive applications
3. Consider using simpler transformation settings

## Saving Settings

To save your current configuration for future use:

```
python voice_transformer.py --save-config my_config.json
```

To load saved settings:

```
python voice_transformer.py --config my_config.json
```

## Troubleshooting During Use

If you experience issues during use:

- **Audio cutting out**: Increase buffer size
- **High latency**: Decrease buffer size or pitch/formant shift intensity
- **Poor voice quality**: Try adjusting pitch and formant shift parameters
- **Program crashes**: Check the logs in `logs/` directory for error information 