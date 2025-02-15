#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime
from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont

# Set up the font directory (adjust if your fonts are elsewhere)
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# Load EB Garamond fonts
REGULAR_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Bold.ttf")
CROSS_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Setup for the Inky display (change driver if needed)
inky_display = auto()

# Load fonts
time_font   = ImageFont.truetype(REGULAR_FONT_PATH, 24)
header_font = ImageFont.truetype(REGULAR_FONT_PATH, 18)
verse_font  = ImageFont.truetype(REGULAR_FONT_PATH, 24)  # Bible verses
bold_font   = ImageFont.truetype(BOLD_FONT_PATH, 36)       # Reference (will be red)
cross_font = ImageFont.truetype(CROSS_FONT_PATH, 36)

def wrap_text(text, font, max_width):
    """Wrap text so that each line fits within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    # Create a temporary image for text measurement.
    temp_img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if temp_draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def bible_clock_loop():
    """Loop forever: update display with the current time and Bible verse from JSON."""
    while True:
        # Create a new blank canvas for full refresh.
        img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
        draw = ImageDraw.Draw(img)

        # Load Bible verses from JSON (update this file to change verses)
        try:
            with open("bible_verse.json") as f:
                verses = json.load(f)
        except Exception as e:
            print("Error loading bible_verse.json:", e)
            verses = {}

        # Get current time and look up the verse.
        now = datetime.now()
        time_key = now.strftime("%H:%M")
        verse_info = verses.get(time_key, "No verse set for this time.")
        if "–" in verse_info:
            reference, verse_text = map(str.strip, verse_info.split("–", 1))
        else:
            reference = verse_info
            verse_text = ""

        # Clear the canvas with white.
        draw.rectangle((0, 0, inky_display.WIDTH, inky_display.HEIGHT), fill=inky_display.WHITE)

        # Top left: Header text (change to "Bible Clock")
        draw.text((10, 10), "Bible Clock", font=header_font, fill=inky_display.BLACK)

        # Top right: Current time display.
        time_str = now.strftime("%H:%M")
        time_bbox = draw.textbbox((0, 0), time_str, font=time_font)
        time_size = (time_bbox[2] - time_bbox[0], time_bbox[3] - time_bbox[1])
        draw.text((inky_display.WIDTH - time_size[0] - 10, 10),
                  time_str, font=time_font, fill=inky_display.BLACK)

        # Draw a horizontal line below the top section.
        draw.line([(0, 40), (inky_display.WIDTH, 40)], fill=inky_display.BLACK, width=2)

        # Center: Bible verse reference (drawn in red).
        ref_bbox = draw.textbbox((0, 0), reference, font=bold_font)
        ref_size = (ref_bbox[2] - ref_bbox[0], ref_bbox[3] - ref_bbox[1])
        ref_x = (inky_display.WIDTH - ref_size[0]) // 2
        ref_y = 60  # position below the line
        draw.text((ref_x, ref_y), reference, font=bold_font, fill=inky_display.RED)

        # Bible verse text (wrapped) in black.
        verse_max_width = inky_display.WIDTH - 40
        lines = wrap_text(verse_text, verse_font, verse_max_width)
        line_height = verse_font.getbbox("Ay")[3]
        verse_start_y = ref_y + ref_size[1] + 10
        for i, line in enumerate(lines):
            line_bbox = draw.textbbox((0, 0), line, font=verse_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (inky_display.WIDTH - line_width) // 2
            draw.text((line_x, verse_start_y + i * (line_height + 4)),
                      line, font=verse_font, fill=inky_display.BLACK)

        # Bottom: Three cross symbols for decoration.
        cross_text = "✝   ✝   ✝"
        cross_bbox = draw.textbbox((0, 0), cross_text, font=cross_font)
        cross_size = (cross_bbox[2] - cross_bbox[0], cross_bbox[3] - cross_bbox[1])
        cross_x = (inky_display.WIDTH - cross_size[0]) // 2
        cross_y = inky_display.HEIGHT - cross_size[1] - 10
        draw.text((cross_x, cross_y), cross_text, font=cross_font, fill=inky_display.BLACK)

        # Use full update (partial_update not supported)
        inky_display.set_image(img)
        inky_display.show()

        # Wait 60 seconds before updating.
        time.sleep(60)

if __name__ == '__main__':
    bible_clock_loop()
