# Galleray

A simple, minimalist image gallery for Linux.

![Galleray Icon](galleray.png)

## Features

- Dark grey modern interface
- Browse images in any directory
- Keyboard navigation (arrow keys or A/D)
- Supports JPG, PNG, GIF, BMP, WebP, TIFF

## Installation

```bash
# Install dependency
pip install PyQt5

# Clone and run
git clone https://github.com/anarchysc/galleray.git
cd galleray
python3 galleray.py
```

## Usage

```bash
# Open the app and select a folder
python3 galleray.py

# Or open directly to a folder
python3 galleray.py /path/to/images
```

### Controls

| Key | Action |
|-----|--------|
| `←` or `A` | Previous image |
| `→` or `D` | Next image |
| `Esc` | Close |

## Desktop Entry

To add to your application menu:

```bash
cp galleray.desktop ~/.local/share/applications/
```

## License

MIT
