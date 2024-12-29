# Desktop Image Monitor

A Python application that monitors your screen for a specific image and plays an alert sound when that image disappears. This can be useful for monitoring status indicators, error messages, or any visual element on your screen.

## Features

- Continuous screen monitoring at configurable intervals
- Audio alerts when target image disappears
- Configurable image matching sensitivity
- User confirmation dialog for alert acknowledgment
- Easy configuration through config.ini

## Prerequisites

- Python 3.8 or higher

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd desktop-monitor
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

The application is configured through `config.ini`:

```ini
[Files]
image_name = image1.png    # Name of the image file to monitor for
mp3_name = for_elise_by_beethoven.mp3       # Name of the sound file to play when image disappears

[Settings]
check_interval = 30        # How often to check for the image (in seconds)
match_threshold = 0.8      # Image matching sensitivity (0.0 to 1.0)
```

### Configuration Parameters:

- `image_name`: The filename of the reference image to monitor for (must be in project directory)
- `mp3_name`: The filename of the alert sound to play (must be in project directory)
- `check_interval`: Time between checks in seconds (higher values reduce CPU usage)
- `match_threshold`: How closely the screen must match the reference image
    - 1.0 = Perfect match required
    - 0.8 = Default, good for most cases
    - 0.6 = More lenient matching
    - Below 0.5 may cause false positives

## Usage

1. Place your reference image (as specified in config.ini) in the project directory
2. Place your alert sound (as specified in config.ini) in the project directory
3. Run the application:
```bash
python monitor.py
```

4. The application will:
    - Monitor your screen at the specified interval
    - Play the alert sound if the image disappears
    - Show a dialog asking if you want to continue monitoring
    - Stop monitoring if you click "No" in the dialog

## Common Use Cases

1. **Error Monitoring**: Monitor for error messages or status indicators
2. **Process Completion**: Monitor for "in progress" indicators
3. **Status Changes**: Monitor for status lights or icons
4. **Availability Checks**: Monitor for "available" or "online" indicators

## Troubleshooting

1. **No module named 'pytesseract'**
   - Ensure you've activated the virtual environment
   - Run `pip install -r requirements.txt`
   
2. **False Positives/Negatives**
   - Adjust the `match_threshold` in config.ini
   - Ensure your reference image is clear and distinctive

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.