#!/usr/bin/env python3
"""
Quaker Quote Display for Inky Impression 7.3"
- Shows a random quote over a random image on startup
- Refreshes when any button is pressed
- Also refreshes every 6 hours via systemd timer (SIGUSR1)
"""

import json
import random
import os
import signal
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from gpiozero import Button

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
QUOTES_FILE = os.path.join(SCRIPT_DIR, "quotes", "quotes.json")
IMAGES_DIR = os.path.join(SCRIPT_DIR, "quotes", "images")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SIZE = 28
SOURCE_FONT_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
OVERLAY_OPACITY = 160
OVERLAY_PADDING = 30
TEXT_MARGIN = 20

# Button GPIO pins (A, B, C, D)
BUTTONS = [5, 6, 16, 24]


def load_quotes():
    with open(QUOTES_FILE, "r") as f:
        return json.load(f)


def pick_random_image():
    extensions = (".jpg", ".jpeg", ".png", ".webp")
    images = [
        f for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith(extensions)
    ]
    if not images:
        raise FileNotFoundError(f"No images found in {IMAGES_DIR}")
    return os.path.join(IMAGES_DIR, random.choice(images))


def crop_to_fill(image, target_width, target_height):
    """Scale image to fill target dimensions, then centre-crop. No stretching."""
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(img_ratio * new_height)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    return image.crop((left, top, left + target_width, top + target_height))


def wrap_text(text, font, draw, max_width):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def draw_overlay(image, quote_text, source_text):
    draw = ImageDraw.Draw(image, "RGBA")

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        source_font = ImageFont.truetype(FONT_PATH, SOURCE_FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()
        source_font = font

    max_text_width = SCREEN_WIDTH - (TEXT_MARGIN * 2) - (OVERLAY_PADDING * 2)

    quote_lines = wrap_text(f'"{quote_text}"', font, draw, max_text_width)
    source_lines = wrap_text(f"— {source_text}", source_font, draw, max_text_width)

    line_spacing = 8
    quote_line_height = FONT_SIZE + line_spacing
    source_line_height = SOURCE_FONT_SIZE + line_spacing

    total_text_height = (
        len(quote_lines) * quote_line_height +
        10 +
        len(source_lines) * source_line_height
    )

    box_width = SCREEN_WIDTH - (TEXT_MARGIN * 2)
    box_height = total_text_height + (OVERLAY_PADDING * 2)
    box_x = TEXT_MARGIN
    box_y = SCREEN_HEIGHT - box_height - TEXT_MARGIN

    draw.rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        fill=(0, 0, 0, OVERLAY_OPACITY)
    )

    y = box_y + OVERLAY_PADDING
    for line in quote_lines:
        draw.text(
            (box_x + OVERLAY_PADDING, y),
            line, font=font,
            fill=(255, 255, 255, 255)
        )
        y += quote_line_height

    y += 10

    for line in source_lines:
        draw.text(
            (box_x + OVERLAY_PADDING, y),
            line,
            font=source_font,
            fill=(220, 220, 220, 255)
        )
        y += source_line_height

    return image


def update_display():
    print("Updating display...")
    quotes = load_quotes()
    quote = random.choice(quotes)
    image_path = pick_random_image()

    print(f"Quote: {quote['text'][:60]}...")
    print(f"Image: {image_path}")

    img = Image.open(image_path).convert("RGB")
    img = crop_to_fill(img, SCREEN_WIDTH, SCREEN_HEIGHT)
    img = img.convert("RGBA")
    img = draw_overlay(img, quote["text"], quote["source"])
    img = img.convert("RGB")

    inky = auto(ask_user=True, verbose=True)
    inky.set_image(img)
    inky.show()
    print("Done.")


def handle_button(btn):
    print(f"Button pressed on GPIO {btn.pin.number} — refreshing display")
    update_display()


def handle_sigusr1(signum, frame):
    print("Received SIGUSR1 — refreshing display")
    update_display()


def main():
    # Register SIGUSR1 handler for timer-triggered refreshes
    signal.signal(signal.SIGUSR1, handle_sigusr1)

    # Show something on startup
    update_display()

    # Set up button listeners
    for pin in BUTTONS:
        btn = Button(pin=pin, pull_up=True, bounce_time=0.25)
        btn.when_pressed = handle_button

    print("Listening for button presses...")
    signal.pause()


if __name__ == "__main__":
    main()
