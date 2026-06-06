#!/usr/bin/env python3
"""
Quaker Quote Display for Inky Impression 7.3"
- Rotates every hour via cron
- Crops image to fill 800x480 without stretching
- Overlays a legible quote with semi-transparent background
"""

import json
import random
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

# --- Configuration ---
QUOTES_FILE = os.path.expanduser("~/quotes/quotes.json")
IMAGES_DIR = os.path.expanduser("~/quotes/images")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SIZE = 28
SOURCE_FONT_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
OVERLAY_OPACITY = 160       # 0-255: higher = darker overlay behind text
OVERLAY_PADDING = 30        # padding inside the text overlay box
TEXT_MARGIN = 20            # margin from screen edges for overlay box


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
        # Image is wider than target — scale by height
        new_height = target_height
        new_width = int(img_ratio * new_height)
    else:
        # Image is taller than target — scale by width
        new_width = target_width
        new_height = int(new_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    return image.crop((left, top, left + target_width, top + target_height))


def wrap_text(text, font, draw, max_width):
    """Wrap text to fit within max_width pixels."""
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
        # Fall back to default if font not found
        font = ImageFont.load_default()
        source_font = font

    max_text_width = SCREEN_WIDTH - (TEXT_MARGIN * 2) - (OVERLAY_PADDING * 2)

    # Wrap quote and source
    quote_lines = wrap_text(f'"{quote_text}"', font, draw, max_text_width)
    source_lines = wrap_text(f"— {source_text}", source_font, draw, max_text_width)

    line_spacing = 8
    quote_line_height = FONT_SIZE + line_spacing
    source_line_height = SOURCE_FONT_SIZE + line_spacing

    total_text_height = (
        len(quote_lines) * quote_line_height +
        10 +  # gap between quote and source
        len(source_lines) * source_line_height
    )

    box_width = SCREEN_WIDTH - (TEXT_MARGIN * 2)
    box_height = total_text_height + (OVERLAY_PADDING * 2)

    # Position overlay at bottom of screen
    box_x = TEXT_MARGIN
    box_y = SCREEN_HEIGHT - box_height - TEXT_MARGIN

    # Draw semi-transparent dark rectangle
    overlay_colour = (0, 0, 0, OVERLAY_OPACITY)
    draw.rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        fill=overlay_colour
    )

    # Draw quote text
    y = box_y + OVERLAY_PADDING
    for line in quote_lines:
        draw.text(
            (box_x + OVERLAY_PADDING, y),
            line,
            font=font,
            fill=(255, 255, 255, 255)
        )
        y += quote_line_height

    y += 10  # gap

    # Draw source text in slightly dimmer white
    for line in source_lines:
        draw.text(
            (box_x + OVERLAY_PADDING, y),
            line,
            font=source_font,
            fill=(220, 220, 220, 255)
        )
        y += source_line_height

    return image


def main():
    # Load data
    quotes = load_quotes()
    quote = random.choice(quotes)
    image_path = pick_random_image()

    print(f"Quote: {quote['text'][:60]}...")
    print(f"Image: {image_path}")

    # Prepare image
    img = Image.open(image_path).convert("RGB")
    img = crop_to_fill(img, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Add overlay — convert to RGBA for transparency, then back to RGB
    img = img.convert("RGBA")
    img = draw_overlay(img, quote["text"], quote["source"])
    img = img.convert("RGB")

    # Send to display
    inky = auto(ask_user=True, verbose=True)
    inky.set_image(img)
    inky.show()

    print("Done.")


if __name__ == "__main__":
    main()
