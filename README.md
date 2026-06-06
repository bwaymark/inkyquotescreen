# Quaker Display

A Raspberry Pi display for the [Pimoroni Inky Impression 7.3"](https://shop.pimoroni.com/products/inky-impression) that shows a rotating Quaker quote overlaid on a background image. Updates every hour.

![Inky Impression 7.3" showing a quote over a landscape image](docs/preview.jpg)

---

## Features

- Randomly selects a quote from your `quotes.json`
- Randomly selects a background image from your images folder
- Centre-crops images to fill 800×480 without stretching or distorting
- Semi-transparent overlay makes the quote legible over any image
- Runs on boot and refreshes every hour via systemd

---

## Requirements

- Raspberry Pi (any 40-pin model)
- Pimoroni Inky Impression 7.3" (800×480)
- Raspberry Pi OS Bookworm or later
- Python 3.7+

---

## Installation

Clone the repo onto your Pi:

```bash
git clone https://github.com/bwaymark/quaker-display.git
cd quaker-display
bash install.sh
```

That's it. The installer will:

1. Copy files to `/home/pi/quaker-display/`
2. Create a Python virtual environment
3. Install `inky` and `pillow`
4. Install and enable the systemd service and timer
5. Run the display immediately

---

## Adding your own content

### Quotes

Edit `/home/pi/quaker-display/quotes/quotes.json`:

```json
[
  {
    "text": "There is that of God in everyone.",
    "source": "George Fox"
  },
  {
    "text": "Your quote here.",
    "source": "Source"
  }
]
```

### Images

Drop `.jpg`, `.png`, or `.webp` files into:

```
/home/pi/quaker-display/quotes/images/
```

Any resolution or aspect ratio works — images are cropped from the centre to fill the screen.

---

## Useful commands

Check the timer is running:
```bash
sudo systemctl status quaker-display.timer
```

View logs:
```bash
sudo journalctl -u quaker-display.service
```

Run manually:
```bash
sudo systemctl start quaker-display.service
```

Stop the hourly rotation:
```bash
sudo systemctl disable quaker-display.timer
sudo systemctl stop quaker-display.timer
```

---

## Configuration

Edit `quaker_display.py` to adjust:

| Variable | Default | Description |
|---|---|---|
| `FONT_SIZE` | 28 | Main quote font size |
| `SOURCE_FONT_SIZE` | 20 | Attribution font size |
| `OVERLAY_OPACITY` | 160 | Darkness of overlay (0–255) |
| `OVERLAY_PADDING` | 30 | Padding inside text box |

---

## Folder structure

```
quaker-display/
  quaker_display.py       # Main script
  install.sh              # Installer
  quotes/
    quotes.json           # Your quotes
    images/               # Your background images
  systemd/
    quaker-display.service
    quaker-display.timer
  README.md
```

---

## Licence

MIT
