# Gall-array

[![gall-array](https://snapcraft.io/gall-array/badge.svg)](https://snapcraft.io/gall-array)
[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/gall-array)

A simple, minimalist image gallery for Linux.

![Gall-array Icon](galleray.png)

## Features

- Dark grey modern interface
- Three view modes:
  - **Gallery** - Navigate with Previous/Next buttons or arrow keys
  - **List** - File list, double-click to view
  - **Grid** - Thumbnail grid with hover magnification preview
- Browse images in any directory
- Keyboard navigation (arrow keys or A/D)
- Supports JPG, PNG, GIF, BMP, WebP, TIFF

## Installation

### Snap Store (Recommended)
```bash
sudo snap install gall-array
```

### From Source
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

## Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/O5O71TOKUE)

## License

MIT

---

Made by [anarchygames.org](https://anarchygames.org)
