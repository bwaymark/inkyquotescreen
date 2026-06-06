# Quaker Display

A Raspberry Pi display for the [Pimoroni Inky Impression 7.3"](https://shop.pimoroni.com/products/inky-impression) that shows a rotating Quaker quote overlaid on a background image.

- Refreshes every 6 hours automatically
- Press any of the four buttons to refresh immediately
- Randomly selects a quote and image each time

---

## Requirements

- Raspberry Pi (any 40-pin model)
- Pimoroni Inky Impression 7.3" (800×480)
- Raspberry Pi OS Bookworm or later
- Python 3.7+

---

## Installation

```bash
git clone https://github.com/bwaymark/inkyquotescreen.git
cd inkyquotescreen
bash install.sh
```

The installer:
1. Copies files to `~/inkyquotescreen/`
2. Creates a Python virtual environment
3. Installs `inky`, `pillow`, and `gpiozero`
4. Installs and enables the systemd service and timer
5. Starts the display immediately

---

## Adding content

### Quotes

Edit `~/inkyquotescreen/quotes/quotes.json`:

```json
[
  {
    "text": "There is that of God in everyone.",
    "source": "George Fox"
  }
]
```

### Images

Drop `.jpg`, `.png`, or `.webp` files into `~/inkyquotescreen/quotes/images/`. Any resolution works — images are centre-cropped to fill 800×480.

---

## Useful commands

```bash
# Check service is running
sudo systemctl status quaker-display.service

# Live logs
sudo journalctl -u quaker-display.service -f

# Trigger a manual refresh
sudo systemctl kill --signal=SIGUSR1 quaker-display.service

# Restart the service
sudo systemctl restart quaker-display.service
```

---

## Updating from GitHub

```bash
cd ~/inkyquotescreen
git pull
bash install.sh
```

Your `quotes.json` and images are preserved on reinstall.

---

## Configuration

Edit `quaker_display.py` to adjust:

| Variable | Default | Description |
|---|---|---|
| `FONT_SIZE` | 28 | Main quote font size |
| `SOURCE_FONT_SIZE` | 20 | Attribution font size |
| `OVERLAY_OPACITY` | 160 | Overlay darkness (0–255) |
| `OVERLAY_PADDING` | 30 | Padding inside text box |

---

## How it works

- `quaker-display.service` — runs permanently, listens for button presses
- `quaker-display.timer` — fires every 6 hours, sends `SIGUSR1` to the running service
- `quaker-refresh.service` — called by the timer, sends the signal

---

## Licence

MIT
