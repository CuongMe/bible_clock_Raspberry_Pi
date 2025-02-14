#!/usr/bin/env python3
import json
import time
from datetime import datetime
from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont

# Configuration: update these paths with your actual font file paths
BOLD_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Setup for the Inky display
inky_display = auto()  # Replace with your specific driver if necessary

# Load fonts
time_font = ImageFont.truetype(REGULAR_FONT_PATH, 24)
header_font = ImageFont.truetype(REGULAR_FONT_PATH, 18)
bold_font = ImageFont.truetype(BOLD_FONT_PATH, 48)
verse_font = ImageFont.truetype(REGULAR_FONT_PATH, 20)
cross_font = ImageFont.truetype(BOLD_FONT_PATH, 36)


# Function for text wrapping
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
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


# Counter to force a full refresh every so often (e.g., every 60 cycles = 1 hour if updating every minute)
full_refresh_interval = 60
cycle = 0

while True:
    # Create a new blank canvas for the update
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)

    # Reload Bible verses from JSON
    with open("bible_verse.json") as f:
        verses = json.load(f)

    now = datetime.now()
    time_key = now.strftime("%H:%M")
    verse_info = verses.get(time_key, "No verse set for this time.")
    if "–" in verse_info:
        reference, verse_text = map(str.strip, verse_info.split("–", 1))
    else:
        reference = verse_info
        verse_text = ""

    # Clear canvas (white)
    draw.rectangle((0, 0, inky_display.WIDTH, inky_display.HEIGHT), fill=inky_display.WHITE)

    # Top left text
    draw.text((10, 10), "connect bluetooth to sync", font=header_font, fill=inky_display.BLACK)

    # Top right current time
    time_str = now.strftime("%H:%M")
    time_bbox = draw.textbbox((0, 0), time_str, font=time_font)
    time_size = (time_bbox[2] - time_bbox[0], time_bbox[3] - time_bbox[1])
    draw.text((inky_display.WIDTH - time_size[0] - 10, 10), time_str, font=time_font, fill=inky_display.BLACK)

    # Center Bible verse reference
    ref_bbox = draw.textbbox((0, 0), reference, font=bold_font)
    ref_size = (ref_bbox[2] - ref_bbox[0], ref_bbox[3] - ref_bbox[1])
    ref_x = (inky_display.WIDTH - ref_size[0]) // 2
    ref_y = (inky_display.HEIGHT // 2) - ref_size[1] - 10
    draw.text((ref_x, ref_y), reference, font=bold_font, fill=inky_display.BLACK)

    # Wrapped Bible verse text below the reference
    verse_max_width = inky_display.WIDTH - 40
    lines = wrap_text(verse_text, verse_font, verse_max_width)
    line_height = verse_font.getbbox("Ay")[3]
    verse_start_y = ref_y + ref_size[1] + 10
    for i, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=verse_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (inky_display.WIDTH - line_width) // 2
        draw.text((line_x, verse_start_y + i * (line_height + 4)), line, font=verse_font, fill=inky_display.BLACK)

    # Bottom three cross symbols
    cross_text = "✝   ✝   ✝"
    cross_bbox = draw.textbbox((0, 0), cross_text, font=cross_font)
    cross_size = (cross_bbox[2] - cross_bbox[0], cross_bbox[3] - cross_bbox[1])
    cross_x = (inky_display.WIDTH - cross_size[0]) // 2
    cross_y = inky_display.HEIGHT - cross_size[1] - 10
    draw.text((cross_x, cross_y), cross_text, font=cross_font, fill=inky_display.BLACK)

    # Update display using partial update for speed.
    # Use a full update occasionally to avoid ghosting.
    if cycle % full_refresh_interval == 0:
        # Perform a full update
        inky_display.set_image(img)
        inky_display.show()
    else:
        # Perform a partial update
        inky_display.set_image(img)
        inky_display.show(partial_update=True)

    cycle += 1
    time.sleep(60)
